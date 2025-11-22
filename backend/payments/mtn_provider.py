"""
MTN Mobile Money provider implementation.
"""

import requests
import uuid
from django.conf import settings
from .providers import PaymentProvider

class MTNProvider(PaymentProvider):
    def __init__(self):
        self.api_url = getattr(settings, 'MTN_MOMO_API_URL', 'https://sandbox.momodeveloper.mtn.com')
        self.api_user = getattr(settings, 'MTN_MOMO_API_USER', 'mock_user')
        self.api_key = getattr(settings, 'MTN_MOMO_API_KEY', 'mock_key')
        self.subscription_key = getattr(settings, 'MTN_MOMO_SUBSCRIPTION_KEY', 'mock_sub_key')
        
    def _get_token(self):
        # In a real implementation, this would fetch an OAuth token
        return "mock_token"

    def initiate_payment(self, amount, currency, metadata=None):
        """
        Request to Pay (Collection).
        """
        transaction_id = str(uuid.uuid4())
        
        # Mocking the request for now since we don't have a live sandbox
        # Real implementation would POST to /collection/v1_0/requesttopay
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "externalId": transaction_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": metadata.get('phone_number', '250780000000')
            },
            "payerMessage": "Contribution",
            "payeeNote": "ChamPlus"
        }
        
        # Simulate success
        return transaction_id, None, {"status": "Pending", "message": "Request accepted"}

    def verify_payment(self, transaction_id):
        """
        Check status of Request to Pay.
        """
        # Real implementation would GET /collection/v1_0/requesttopay/{transaction_id}
        return 'pending' # Mock status
