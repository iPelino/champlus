"""
Bank Transfer provider implementation.
"""

import uuid
from .providers import PaymentProvider

class BankTransferProvider(PaymentProvider):
    def initiate_payment(self, amount, currency, metadata=None):
        """
        Initiate a manual bank transfer.
        This doesn't call an external API yet, but prepares the transaction for manual verification.
        """
        transaction_id = str(uuid.uuid4())
        
        # In a real bank integration, we might call an API here to get a reference number
        # For now, we just generate a reference and return success
        
        return transaction_id, None, {"status": "Pending Approval", "message": "Please upload proof of payment"}

    def verify_payment(self, transaction_id):
        """
        Check status. For manual transfers, this is always 'pending' until admin action.
        """
        return 'pending_approval'
