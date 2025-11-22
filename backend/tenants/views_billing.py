"""
Billing views for subscription management.
"""

from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Tenant

class SubscriptionStatusView(views.APIView):
    """
    Get current subscription status.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tenant = request.tenant
        if not tenant:
            return Response({"error": "No tenant found"}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            "status": tenant.subscription_status,
            "trial_ends_at": tenant.trial_ends_at,
            "subscription_ends_at": tenant.subscription_ends_at,
            "is_active": tenant.is_active
        })

class CreateCheckoutSessionView(views.APIView):
    """
    Mock endpoint to create a checkout session.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # In a real app, this would call Stripe API
        return Response({
            "checkout_url": "https://checkout.stripe.com/mock-session",
            "session_id": "cs_test_mock123"
        })

class BillingPortalView(views.APIView):
    """
    Mock endpoint to get billing portal URL.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # In a real app, this would call Stripe API
        return Response({
            "url": "https://billing.stripe.com/mock-portal"
        })

class MockWebhookView(views.APIView):
    """
    Mock webhook to simulate successful payment.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # Simulate payment success
        tenant_id = request.data.get('tenant_id')
        if not tenant_id:
            return Response({"error": "Tenant ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            tenant.subscription_status = 'active'
            tenant.subscription_ends_at = timezone.now() + timedelta(days=30)
            tenant.save()
            return Response({"message": "Subscription activated"})
        except Tenant.DoesNotExist:
            return Response({"error": "Tenant not found"}, status=status.HTTP_404_NOT_FOUND)
