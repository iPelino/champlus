from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from .models import Loan, Repayment
from .serializers import LoanSerializer, RepaymentSerializer
from financials.models import Transaction
from notifications.utils import send_notification

class LoanListCreateView(generics.ListCreateAPIView):
    """
    List loans or apply for a new loan.
    """
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        if not tenant:
            return Loan.objects.none()
        group = tenant.groups.first()
        
        # Members see their own loans, admins see all
        # For simplicity, let's return all for now, or filter by user if not admin
        # Assuming standard member access:
        return Loan.objects.filter(group=group)

    def perform_create(self, serializer):
        tenant = self.request.tenant
        group = tenant.groups.first()
        serializer.save(group=group, borrower=self.request.user)
        
        # Notify admins
        # (In a real app, we'd find admins and email them)
        pass

class LoanDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a loan (e.g., approve/reject).
    """
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        if not tenant:
            return Loan.objects.none()
        group = tenant.groups.first()
        return Loan.objects.filter(group=group)

class LoanActionView(views.APIView):
    """
    Handle loan actions: approve, reject, disburse.
    """
    permission_classes = [permissions.IsAuthenticated] # Check role manually or use IsAdminUser if staff
    
    def post(self, request, pk, action):
        # Check if user is admin of the group
        try:
            loan = Loan.objects.get(pk=pk)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

        # Verify group admin role
        from members.models import GroupMembership
        is_admin = GroupMembership.objects.filter(
            user=request.user, 
            group=loan.group, 
            role='admin',
            is_active=True
        ).exists()
        
        if not is_admin:
             return Response({"error": "Only group admins can perform this action"}, status=status.HTTP_403_FORBIDDEN)
            
        if action == 'approve':
            if loan.status != 'requested':
                return Response({"error": "Loan is not in requested state"}, status=status.HTTP_400_BAD_REQUEST)
            
            loan.status = 'approved'
            loan.approved_by = request.user
            loan.approved_at = timezone.now()
            loan.save()
            
            send_notification(
                loan.borrower,
                "Loan Approved",
                f"Your loan of {loan.amount} has been approved.",
                'email'
            )
            return Response({"status": "approved"})
            
        elif action == 'reject':
            if loan.status != 'requested':
                return Response({"error": "Loan is not in requested state"}, status=status.HTTP_400_BAD_REQUEST)
                
            loan.status = 'rejected'
            loan.save()
            return Response({"message": "Loan rejected"})
            
        elif action == 'disburse':
            if loan.status != 'approved':
                return Response({"error": "Loan must be approved before disbursement"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if approval is needed (e.g., amount > 1000)
            # For this sprint, we'll say ALL disbursements need Maker-Checker approval
            from approvals.service import ApprovalService
            
            ApprovalService.request_approval(
                user=request.user,
                action_type='disburse_loan',
                content_object=loan,
                data={'amount': str(loan.amount)}
            )
            
            return Response({"message": "Disbursement request created. Pending secondary approval."})
            
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class RepaymentCreateView(generics.CreateAPIView):
    """
    Record a loan repayment.
    """
    serializer_class = RepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        loan_id = self.request.data.get('loan')
        loan = Loan.objects.get(pk=loan_id)
        amount = serializer.validated_data['amount']
        
        with transaction.atomic():
            repayment = serializer.save(recorded_by=self.request.user)
            
            # Update loan amount paid
            loan.amount_paid += amount
            if loan.amount_paid >= loan.total_amount_payable:
                loan.status = 'paid'
            loan.save()
            
                # Record transaction (Money entering the group)
            Transaction.objects.create(
                group=loan.group,
                transaction_type='contribution', # Repayment is income
                amount=amount,
                balance_after=0, # Simplified
                transaction_date=timezone.now().date(),
                description=f"Loan Repayment from {loan.borrower.get_full_name()}",
                created_by=self.request.user
            )
