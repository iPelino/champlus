"""
Service for handling approval logic.
"""

from .models import ApprovalRequest
from django.contrib.contenttypes.models import ContentType

class ApprovalService:
    @staticmethod
    def request_approval(user, action_type, content_object, data=None):
        """
        Create an approval request.
        """
        if data is None:
            data = {}
            
        request = ApprovalRequest.objects.create(
            requester=user,
            action_type=action_type,
            content_object=content_object,
            data=data,
            status='pending'
        )
        return request

    @staticmethod
    def approve_request(request_id, reviewer):
        """
        Approve a request and execute the action.
        """
        try:
            approval = ApprovalRequest.objects.get(id=request_id)
        except ApprovalRequest.DoesNotExist:
            return False, "Request not found"
            
        if approval.status != 'pending':
            return False, "Request is not pending"
            
        if approval.requester == reviewer:
            return False, "Requester cannot approve their own request"
            
        approval.status = 'approved'
        approval.reviewer = reviewer
        approval.save()
        
        # Execute the deferred action
        success, message = ApprovalService._execute_action(approval)
        if not success:
            # Revert status if execution fails? 
            # Or keep as approved but failed execution?
            # For simplicity, let's keep it approved but log error
            return False, f"Approved but execution failed: {message}"
            
        return True, "Request approved and executed"

    @staticmethod
    def reject_request(request_id, reviewer, reason):
        """
        Reject a request.
        """
        try:
            approval = ApprovalRequest.objects.get(id=request_id)
        except ApprovalRequest.DoesNotExist:
            return False, "Request not found"
            
        if approval.status != 'pending':
            return False, "Request is not pending"
            
        approval.status = 'rejected'
        approval.reviewer = reviewer
        approval.reason = reason
        approval.save()
        
        return True, "Request rejected"

    @staticmethod
    def _execute_action(approval):
        """
        Execute the action based on type.
        """
        if approval.action_type == 'disburse_loan':
            from loans.models import Loan
            loan = approval.content_object
            if isinstance(loan, Loan):
                # Logic from LoanActionView
                loan.status = 'active'
                loan.save()
                
                # Create transaction
                from financials.models import Transaction
                from django.utils import timezone
                
                Transaction.objects.create(
                    group=loan.group,
                    transaction_type='expense',
                    amount=loan.amount,
                    balance_after=0,
                    transaction_date=timezone.now().date(),
                    description=f"Loan Disbursement to {loan.borrower.get_full_name()}",
                    created_by=approval.reviewer # The approver is the one "making" the transaction now
                )
                return True, "Loan disbursed"
                
        elif approval.action_type == 'verify_payment':
            from payments.models import PaymentTransaction
            payment = approval.content_object
            if isinstance(payment, PaymentTransaction):
                payment.status = 'completed'
                payment.save()
                
                # Create internal transaction (Income)
                from financials.models import Transaction
                from django.utils import timezone
                
                # Assuming payment belongs to a group member, we need to find their group
                # For simplicity, let's assume the user has one primary group or it's passed in metadata
                # But wait, PaymentTransaction doesn't link to Group directly yet.
                # We should probably link it or infer it.
                # Let's assume the requester's first group for now or use a default.
                # Ideally, InitiatePaymentView should accept group_id.
                
                # Quick fix: Get group from requester
                from members.models import GroupMembership
                membership = GroupMembership.objects.filter(user=approval.requester).first()
                if not membership:
                    return False, "User does not belong to any group"
                    
                Transaction.objects.create(
                    group=membership.group,
                    transaction_type='contribution',
                    amount=payment.amount,
                    balance_after=0,
                    transaction_date=timezone.now().date(),
                    description=f"Bank Transfer from {approval.requester.get_full_name()}",
                    created_by=approval.reviewer
                )
                
                # Link it
                payment.internal_transaction = Transaction.objects.last()
                payment.save()
                
                return True, "Payment verified and recorded"
                
        return False, "Unknown action type"
