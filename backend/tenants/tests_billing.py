"""
Tests for billing and subscription functionality.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, UserProfile
from django.utils import timezone
from datetime import timedelta

class BillingTest(TestCase):
    """Test cases for billing functionality."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create tenant
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            subdomain="testtenant",
            slug="test-tenant",
            subscription_status='trial',
            trial_ends_at=timezone.now() + timedelta(days=14),
            is_active=True
        )
        
        # Create group
        self.group = Group.objects.create(
            name="Test Group",
            tenant=self.tenant,
            contribution_amount=1000.00
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="password"
        )
        UserProfile.objects.create(user=self.admin_user)
        
        # Create admin membership
        GroupMembership.objects.create(
            user=self.admin_user,
            group=self.group,
            role='admin'
        )
        
        # URLs
        self.status_url = reverse('subscription-status')
        self.checkout_url = reverse('create-checkout')
        self.portal_url = reverse('billing-portal')
        self.webhook_url = reverse('mock-webhook')
        
    def test_subscription_status(self):
        """Test retrieving subscription status."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(
            self.status_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'trial')
        self.assertTrue(response.data['is_active'])
        
    def test_create_checkout_session(self):
        """Test creating a mock checkout session."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(
            self.checkout_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('checkout_url', response.data)
        
    def test_billing_portal(self):
        """Test accessing mock billing portal."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(
            self.portal_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('url', response.data)
        
    def test_mock_webhook(self):
        """Test mock webhook for subscription activation."""
        response = self.client.post(
            self.webhook_url,
            {'tenant_id': str(self.tenant.id)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.subscription_status, 'active')
        self.assertIsNotNone(self.tenant.subscription_ends_at)
