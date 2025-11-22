"""
Tests for payment integration.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from payments.models import PaymentTransaction
from unittest.mock import patch, MagicMock

class PaymentTest(TestCase):
    """Test cases for payment integration."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="payer",
            email="payer@test.com",
            password="password"
        )
        self.initiate_url = reverse('payment-initiate')
        self.stripe_webhook_url = reverse('stripe-webhook')
        self.mtn_callback_url = reverse('mtn-callback')
        
    @patch('payments.stripe_provider.stripe.PaymentIntent.create')
    def test_initiate_stripe_payment(self, mock_create):
        """Test initiating a Stripe payment."""
        self.client.force_authenticate(user=self.user)
        
        # Mock Stripe response
        mock_intent = MagicMock()
        mock_intent.id = "pi_12345"
        mock_intent.client_secret = "secret_123"
        mock_create.return_value = mock_intent
        
        data = {
            "provider": "stripe",
            "amount": "100.00",
            "currency": "USD"
        }
        
        response = self.client.post(self.initiate_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_id'], "pi_12345")
        
        # Verify DB record
        self.assertEqual(PaymentTransaction.objects.count(), 1)
        txn = PaymentTransaction.objects.first()
        self.assertEqual(txn.provider, 'stripe')
        self.assertEqual(txn.provider_transaction_id, "pi_12345")
        self.assertEqual(txn.status, 'pending')
        
    @patch('payments.mtn_provider.requests.post')
    def test_initiate_mtn_payment(self, mock_post):
        """Test initiating an MTN payment."""
        self.client.force_authenticate(user=self.user)
        
        # Mock MTN response (not strictly needed as our mock provider simulates it, 
        # but good if we were testing the real provider logic more deeply)
        # Our MTNProvider currently mocks the logic internally, so we don't strictly need to patch requests.post
        # UNLESS we change MTNProvider to actually call requests.
        # For now, let's just test the view logic.
        
        data = {
            "provider": "mtn",
            "amount": "5000.00",
            "currency": "RWF",
            "phone_number": "250788888888"
        }
        
        response = self.client.post(self.initiate_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('transaction_id', response.data)
        
        # Verify DB record
        self.assertEqual(PaymentTransaction.objects.count(), 1)
        txn = PaymentTransaction.objects.first()
        self.assertEqual(txn.provider, 'mtn')
        self.assertEqual(txn.status, 'pending')
        
    @patch('payments.views.stripe.Webhook.construct_event')
    def test_stripe_webhook(self, mock_construct_event):
        """Test Stripe webhook handling."""
        # Create pending transaction
        PaymentTransaction.objects.create(
            provider='stripe',
            provider_transaction_id="pi_success",
            amount="100.00",
            status='pending'
        )
        
        # Mock event
        mock_event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_success'
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        response = self.client.post(
            self.stripe_webhook_url, 
            {'data': 'dummy'}, 
            format='json',
            HTTP_STRIPE_SIGNATURE='dummy_sig'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status update
        txn = PaymentTransaction.objects.get(provider_transaction_id="pi_success")
        self.assertEqual(txn.status, 'completed')
        
    def test_mtn_callback(self):
        """Test MTN callback handling."""
        # Create pending transaction
        PaymentTransaction.objects.create(
            provider='mtn',
            provider_transaction_id="mtn_123",
            amount="5000.00",
            status='pending'
        )
        
        data = {
            "externalId": "mtn_123",
            "status": "SUCCESSFUL"
        }
        
        response = self.client.post(self.mtn_callback_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status update
        txn = PaymentTransaction.objects.get(provider_transaction_id="mtn_123")
        self.assertEqual(txn.status, 'completed')
