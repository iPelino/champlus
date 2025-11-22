"""
Stripe payment provider implementation.
"""

import stripe
from django.conf import settings
from .providers import PaymentProvider

class StripeProvider(PaymentProvider):
    def __init__(self):
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_mock')

    def initiate_payment(self, amount, currency, metadata=None):
        """
        Create a Stripe PaymentIntent.
        Amount is in cents/smallest unit for Stripe.
        """
        try:
            # Convert amount to smallest unit (e.g., cents)
            # Assuming amount is Decimal
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True},
            )
            
            return intent.id, intent.client_secret, intent
            
        except Exception as e:
            print(f"Stripe Error: {e}")
            return None, None, str(e)

    def verify_payment(self, transaction_id):
        """
        Retrieve PaymentIntent status.
        """
        try:
            intent = stripe.PaymentIntent.retrieve(transaction_id)
            status_map = {
                'succeeded': 'completed',
                'processing': 'pending',
                'requires_payment_method': 'pending',
                'canceled': 'failed',
            }
            return status_map.get(intent.status, 'pending')
        except Exception as e:
            return 'failed'
