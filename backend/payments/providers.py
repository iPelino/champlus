"""
Abstract base class for payment providers.
"""

from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    """
    Interface for payment providers (Stripe, MTN, etc.)
    """
    
    @abstractmethod
    def initiate_payment(self, amount, currency, metadata=None):
        """
        Initiate a payment request.
        Returns: (transaction_id, client_secret/approval_url, raw_response)
        """
        pass
        
    @abstractmethod
    def verify_payment(self, transaction_id):
        """
        Check status of a payment.
        Returns: status (pending, completed, failed)
        """
        pass
