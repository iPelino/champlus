"""
Tests for approval workflows.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, UserProfile
from loans.models import Loan
from approvals.models import ApprovalRequest
from decimal import Decimal

class ApprovalTest(TestCase):
    """Test cases for approval workflows."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create tenant & group
        self.tenant = Tenant.objects.create(name="Test Tenant", subdomain="testtenant")
        self.group = Group.objects.create(
            name="Test Group", 
            tenant=self.tenant,
            contribution_amount=Decimal('1000.00')
        )
        
        # Create Maker (Admin 1)
        self.maker = User.objects.create_user(username="maker", email="maker@test.com", password="password")
        UserProfile.objects.create(user=self.maker)
        GroupMembership.objects.create(user=self.maker, group=self.group, role='admin')
        
        # Create Checker (Admin 2)
        self.checker = User.objects.create_user(username="checker", email="checker@test.com", password="password")
        UserProfile.objects.create(user=self.checker)
        GroupMembership.objects.create(user=self.checker, group=self.group, role='admin')
        
        # Create Borrower
        self.borrower = User.objects.create_user(username="borrower", email="borrower@test.com", password="password")
        UserProfile.objects.create(user=self.borrower)
        GroupMembership.objects.create(user=self.borrower, group=self.group, role='member')
        
        # Create Approved Loan ready for disbursement
        self.loan = Loan.objects.create(
            group=self.group,
            borrower=self.borrower,
            amount=Decimal('10000.00'),
            interest_rate=Decimal('10.00'),
            duration_months=6,
            status='approved'
        )
        
    def test_maker_checker_flow(self):
        """Test that disbursement requires approval."""
        
        # 1. Maker requests disbursement
        self.client.force_authenticate(user=self.maker)
        url = reverse('loan-action', kwargs={'pk': self.loan.id, 'action': 'disburse'})
        response = self.client.post(url, HTTP_HOST='testtenant.testserver')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Disbursement request created", response.data['message'])
        
        # Verify loan is NOT active yet
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.status, 'approved')
        
        # Verify ApprovalRequest created
        self.assertEqual(ApprovalRequest.objects.count(), 1)
        approval = ApprovalRequest.objects.first()
        self.assertEqual(approval.status, 'pending')
        self.assertEqual(approval.requester, self.maker)
        
        # 2. Maker tries to approve their own request (Should fail)
        action_url = reverse('approval-action', kwargs={'pk': approval.id, 'action': 'approve'})
        response = self.client.post(action_url, HTTP_HOST='testtenant.testserver')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Requester cannot approve", response.data['error'])
        
        # 3. Checker approves request
        self.client.force_authenticate(user=self.checker)
        response = self.client.post(action_url, HTTP_HOST='testtenant.testserver')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify request approved
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'approved')
        self.assertEqual(approval.reviewer, self.checker)
        
        # Verify Loan is now ACTIVE
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.status, 'active')
