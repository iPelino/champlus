"""
Tests for bank transfer integration.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from payments.models import PaymentTransaction
from approvals.models import ApprovalRequest
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal

class BankTransferTest(TestCase):
    """Test cases for bank transfer."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Setup Tenant & Group
        self.tenant = Tenant.objects.create(name="Test Tenant", subdomain="testtenant")
        self.group = Group.objects.create(
            name="Test Group", 
            tenant=self.tenant,
            contribution_amount=Decimal('1000.00')
        )
        
        # Create Payer (Member)
        self.payer = User.objects.create_user(username="payer", email="payer@test.com", password="password")
        UserProfile.objects.create(user=self.payer)
        GroupMembership.objects.create(user=self.payer, group=self.group, role='member')
        
        # Create Admin (Approver)
        self.admin = User.objects.create_user(username="admin", email="admin@test.com", password="password")
        UserProfile.objects.create(user=self.admin)
        GroupMembership.objects.create(user=self.admin, group=self.group, role='admin')
        
        self.initiate_url = reverse('payment-initiate')
        
    def test_manual_bank_transfer_flow(self):
        """Test uploading proof and admin verification."""
        self.client.force_authenticate(user=self.payer)
        
        # 1. Upload Proof
        proof = SimpleUploadedFile("proof.jpg", b"file_content", content_type="image/jpeg")
        data = {
            "provider": "bank_transfer",
            "amount": "5000.00",
            "currency": "RWF",
            "proof_of_payment": proof
        }
        
        response = self.client.post(self.initiate_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify PaymentTransaction created
        self.assertEqual(PaymentTransaction.objects.count(), 1)
        txn = PaymentTransaction.objects.first()
        self.assertEqual(txn.provider, 'bank_transfer')
        self.assertEqual(txn.status, 'pending_approval')
        self.assertTrue(txn.proof_of_payment)
        
        # Verify ApprovalRequest created
        self.assertEqual(ApprovalRequest.objects.count(), 1)
        approval = ApprovalRequest.objects.first()
        self.assertEqual(approval.action_type, 'verify_payment')
        self.assertEqual(approval.status, 'pending')
        
        # 2. Admin Approves
        self.client.force_authenticate(user=self.admin)
        action_url = reverse('approval-action', kwargs={'pk': approval.id, 'action': 'approve'})
        response = self.client.post(action_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Payment Completed
        txn.refresh_from_db()
        self.assertEqual(txn.status, 'completed')
        self.assertIsNotNone(txn.internal_transaction)
        
        # Verify Ledger Updated
        self.assertEqual(txn.internal_transaction.amount, Decimal('5000.00'))
        self.assertEqual(txn.internal_transaction.transaction_type, 'contribution')
