"""
Tests for the financials app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, UserProfile
from financials.models import Contribution, Expense, Transaction
from django.utils import timezone
from datetime import timedelta

class FinancialsTest(TestCase):
    """Test cases for financial operations."""
    
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
        
        # Create admin membership
        GroupMembership.objects.create(
            user=self.admin_user,
            group=self.group,
            role='admin'
        )
        
        # URLs
        self.contribution_url = reverse('contribution-list')
        self.expense_url = reverse('expense-list')
        self.ledger_url = reverse('ledger')
        
    def test_log_contribution(self):
        """Test logging a contribution."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'amount': 1000.00,
            'payment_method': 'mpesa',
            'reference_number': 'REF123',
            'contribution_date': timezone.now().date(),
            'period_start': timezone.now().date(),
            'period_end': timezone.now().date() + timedelta(days=30),
            'notes': 'Monthly contribution'
        }
        
        response = self.client.post(
            self.contribution_url,
            data,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contribution.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 1)
        
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.amount, 1000.00)
        self.assertEqual(transaction.balance_after, 1000.00)
        self.assertEqual(transaction.transaction_type, 'contribution')
        
    def test_log_expense(self):
        """Test logging an expense."""
        # First log a contribution to have funds
        self.test_log_contribution()
        
        data = {
            'description': 'Office Supplies',
            'category': 'administrative',
            'amount': 200.00,
            'expense_date': timezone.now().date(),
            'notes': 'Pens and paper'
        }
        
        response = self.client.post(
            self.expense_url,
            data,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 2) # 1 contrib + 1 expense
        
        expense_transaction = Transaction.objects.order_by('-created_at').first()
        self.assertEqual(expense_transaction.amount, -200.00)
        self.assertEqual(expense_transaction.balance_after, 800.00) # 1000 - 200
        self.assertEqual(expense_transaction.transaction_type, 'expense')
        
    def test_view_ledger(self):
        """Test viewing the ledger."""
        # Log contribution and expense
        self.test_log_expense()
        
        response = self.client.get(
            self.ledger_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verify order (newest first)
        self.assertEqual(response.data[0]['transaction_type'], 'expense')
        self.assertEqual(response.data[1]['transaction_type'], 'contribution')
