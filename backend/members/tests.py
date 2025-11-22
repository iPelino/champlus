"""
Tests for the members app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, GroupInvitation, UserProfile
from django.utils import timezone
import uuid

class MemberInvitationTest(TestCase):
    """Test cases for member invitations."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create tenant
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            subdomain="testtenant",
            slug="test-tenant"
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
        self.send_url = reverse('send-invitation')
        self.accept_url = reverse('accept-invitation')
        self.list_url = reverse('member-list')
        
    def test_send_invitation(self):
        """Test sending an invitation."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Set tenant context via host
        response = self.client.post(
            self.send_url,
            {
                'email': 'newmember@test.com',
                'role': 'member',
                'message': 'Join us!'
            },
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GroupInvitation.objects.count(), 1)
        invitation = GroupInvitation.objects.first()
        self.assertEqual(invitation.email, 'newmember@test.com')
        self.assertEqual(invitation.status, 'pending')
        
    def test_accept_invitation_new_user(self):
        """Test accepting an invitation as a new user."""
        # Create invitation
        invitation = GroupInvitation.objects.create(
            group=self.group,
            invited_by=self.admin_user,
            email='newmember@test.com',
            role='member',
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
        
        response = self.client.post(self.accept_url, {
            'token': invitation.token,
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'Member'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user created
        self.assertTrue(User.objects.filter(email='newmember@test.com').exists())
        new_user = User.objects.get(email='newmember@test.com')
        
        # Verify membership created
        self.assertTrue(GroupMembership.objects.filter(user=new_user, group=self.group).exists())
        
        # Verify invitation updated
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'accepted')
        self.assertEqual(invitation.invited_user, new_user)
        
    def test_list_members(self):
        """Test listing group members."""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(
            self.list_url,
            HTTP_HOST='testtenant.testserver'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Only admin so far
        self.assertEqual(response.data[0]['user']['email'], 'admin@test.com')
