"""
Tests for the loans app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, UserProfile
from loans.models import Loan, Repayment
from financials.models import Transaction
from decimal import Decimal

class LoanTest(TestCase):
    """Test cases for loan management."""
    
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
            password="password",
            first_name="Admin",
            last_name="User"
        )
        UserProfile.objects.create(user=self.admin_user)
        GroupMembership.objects.create(user=self.admin_user, group=self.group, role='admin')
        
        # Create member user
        self.member_user = User.objects.create_user(
            username="member",
            email="member@test.com",
            password="password",
            first_name="Member",
            last_name="User"
        )
        UserProfile.objects.create(user=self.member_user)
        GroupMembership.objects.create(user=self.member_user, group=self.group, role='member')
        
        # URLs
        self.loan_list_url = reverse('loan-list')
        self.repayment_url = reverse('repayment-create')
        
    def test_loan_application(self):
        """Test applying for a loan."""
        self.client.force_authenticate(user=self.member_user)
        
        data = {
            "amount": "10000.00",
            "interest_rate": "10.00",
            "duration_months": 6
        }
        
        response = self.client.post(
            self.loan_list_url,
            data,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)
        loan = Loan.objects.first()
        self.assertEqual(loan.status, 'requested')
        self.assertEqual(loan.total_amount_payable, Decimal('11000.00')) # 10k + 10%
        
    def test_loan_approval_and_disbursement(self):
        """Test approving and disbursing a loan."""
        # Create loan
        loan = Loan.objects.create(
            group=self.group,
            borrower=self.member_user,
            amount=Decimal('10000.00'),
            interest_rate=Decimal('10.00'),
            duration_months=6
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Approve
        approve_url = reverse('loan-action', kwargs={'pk': loan.id, 'action': 'approve'})
        response = self.client.post(approve_url, HTTP_HOST='testtenant.testserver')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'approved')
        
        # Disburse
        disburse_url = reverse('loan-action', kwargs={'pk': loan.id, 'action': 'disburse'})
        response = self.client.post(disburse_url, HTTP_HOST='testtenant.testserver')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'active')
        
        # Check transaction
        self.assertEqual(Transaction.objects.count(), 1)
        txn = Transaction.objects.first()
        self.assertEqual(txn.transaction_type, 'expense')
        self.assertEqual(txn.amount, Decimal('10000.00'))
        
    def test_repayment(self):
        """Test repaying a loan."""
        # Create active loan
        loan = Loan.objects.create(
            group=self.group,
            borrower=self.member_user,
            amount=Decimal('10000.00'),
            interest_rate=Decimal('10.00'),
            duration_months=6,
            status='active',
            total_amount_payable=Decimal('11000.00')
        )
        
        self.client.force_authenticate(user=self.member_user)
        
        data = {
            "loan": loan.id,
            "amount": "5000.00"
        }
        
        response = self.client.post(
            self.repayment_url,
            data,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        loan.refresh_from_db()
        self.assertEqual(loan.amount_paid, Decimal('5000.00'))
        
        # Full repayment
        data['amount'] = "6000.00"
        response = self.client.post(
            self.repayment_url,
            data,
            HTTP_HOST='testtenant.testserver'
        )
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'paid')
        self.assertEqual(loan.amount_paid, Decimal('11000.00'))
