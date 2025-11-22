from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from .models import PaymentTransaction
from .stripe_provider import StripeProvider
from .mtn_provider import MTNProvider
from .bank_provider import BankTransferProvider
import stripe

class InitiatePaymentView(views.APIView):
    """
    Initiate a payment.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser] # Support file uploads
    
    def post(self, request):
        provider_name = request.data.get('provider', 'stripe')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'RWF')
        phone_number = request.data.get('phone_number') # For MTN
        proof_of_payment = request.FILES.get('proof_of_payment') # For Bank Transfer
        
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Select provider
        if provider_name == 'stripe':
            provider = StripeProvider()
        elif provider_name == 'mtn':
            provider = MTNProvider()
        elif provider_name == 'bank_transfer':
            provider = BankTransferProvider()
        else:
            return Response({"error": "Invalid provider"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Metadata
        metadata = {
            'user_id': request.user.id,
            'phone_number': phone_number
        }
        
        # Initiate
        txn_id, client_secret, raw_response = provider.initiate_payment(
            float(amount), 
            currency, 
            metadata
        )
        
        if not txn_id:
            return Response({"error": "Payment initiation failed", "details": raw_response}, status=status.HTTP_400_BAD_REQUEST)
            
        # Save transaction
        status_val = 'pending'
        if provider_name == 'bank_transfer':
            status_val = 'pending_approval'
            
        txn = PaymentTransaction.objects.create(
            provider=provider_name,
            provider_transaction_id=txn_id,
            amount=amount,
            currency=currency,
            status=status_val,
            metadata=metadata,
            proof_of_payment=proof_of_payment
        )
        
        # If bank transfer, trigger approval workflow
        if provider_name == 'bank_transfer':
            from approvals.service import ApprovalService
            ApprovalService.request_approval(
                user=request.user,
                action_type='verify_payment',
                content_object=txn,
                data={'amount': str(amount)}
            )
        
        return Response({
            "transaction_id": txn_id,
            "client_secret": client_secret, # For Stripe frontend
            "message": "Payment initiated"
        })

class StripeWebhookView(views.APIView):
    """
    Handle Stripe webhooks.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_successful_payment(payment_intent['id'])
            
        return Response({"status": "success"})
        
    def _handle_successful_payment(self, txn_id):
        try:
            txn = PaymentTransaction.objects.get(provider_transaction_id=txn_id)
            txn.status = 'completed'
            txn.save()
            
            # Here we would create the internal Transaction and update Ledger
            # For now, just marking as completed
        except PaymentTransaction.DoesNotExist:
            pass

class MTNCallbackView(views.APIView):
    """
    Handle MTN callbacks.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # MTN sends JSON payload with status
        data = request.data
        external_id = data.get('externalId')
        status_code = data.get('status')
        
        if external_id and status_code == 'SUCCESSFUL':
            try:
                txn = PaymentTransaction.objects.get(provider_transaction_id=external_id)
                txn.status = 'completed'
                txn.save()
            except PaymentTransaction.DoesNotExist:
                pass
                
        return Response({"status": "received"})
