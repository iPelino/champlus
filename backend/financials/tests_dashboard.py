"""
Tests for financial dashboards and reporting.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, UserProfile
from financials.models import Contribution, Transaction
from django.utils import timezone
from datetime import timedelta

class DashboardTest(TestCase):
    """Test cases for dashboards and reports."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create tenant
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            subdomain="testtenant",
            slug="test-tenant",
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
        GroupMembership.objects.create(user=self.admin_user, group=self.group, role='admin')
        
        # Create defaulter user
        self.defaulter_user = User.objects.create_user(
            username="defaulter",
            email="defaulter@test.com",
            password="password"
        )
        UserProfile.objects.create(user=self.defaulter_user)
        GroupMembership.objects.create(user=self.defaulter_user, group=self.group, role='member')
        
        # URLs
        self.dashboard_url = reverse('member-dashboard')
        self.defaulters_url = reverse('defaulter-list')
        self.export_url = reverse('statement-export')
        
    def test_member_dashboard(self):
        """Test member dashboard data."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create contribution
        contribution = Contribution.objects.create(
            group=self.group,
            member=self.admin_user,
            amount=1000.00,
            contribution_date=timezone.now().date(),
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timedelta(days=30),
            status='approved'
        )
        
        Transaction.objects.create(
            group=self.group,
            transaction_type='contribution',
            contribution=contribution,
            amount=1000.00,
            balance_after=1000.00,
            transaction_date=timezone.now().date(),
            description="Contrib",
            created_by=self.admin_user
        )
        
        response = self.client.get(
            self.dashboard_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_contributions'], 1000.00)
        self.assertEqual(len(response.data['recent_transactions']), 1)
        
    def test_defaulter_list(self):
        """Test defaulter identification."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Admin has contributed (in setUp via test_member_dashboard logic above, but let's be explicit)
        Contribution.objects.create(
            group=self.group,
            member=self.admin_user,
            amount=1000.00,
            contribution_date=timezone.now().date(),
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timedelta(days=30),
            status='approved'
        )
        
        # Defaulter has NOT contributed
        
        response = self.client.get(
            self.defaulters_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Should list paginated results or list
        # Since ListAPIView returns paginated response by default if pagination is set?
        # Let's assume default pagination is NOT set or check response structure.
        # Based on previous tests, it might be paginated if global settings apply.
        # But ListAPIView usually returns a list if PAGE_SIZE is not set.
        # Wait, earlier I found DEFAULT_PAGINATION_CLASS was NOT set.
        
        self.assertEqual(response.data[0]['email'], 'defaulter@test.com')
        
    def test_statement_export(self):
        """Test CSV export."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(
            self.export_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="statement.csv"', response['Content-Disposition'])
