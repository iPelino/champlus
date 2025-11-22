"""
Tests for notifications and reminders.
"""

from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import GroupMembership, UserProfile
from notifications.models import Notification
from notifications.utils import send_notification
from django.core.management import call_command
from django.utils import timezone

class NotificationTest(TestCase):
    """Test cases for notifications."""
    
    def setUp(self):
        # Create tenant and group
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            subdomain="testtenant",
            slug="test-tenant",
            is_active=True
        )
        self.group = Group.objects.create(
            name="Test Group",
            tenant=self.tenant,
            contribution_amount=1000.00
        )
        
        # Create user
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        UserProfile.objects.create(user=self.user)
        GroupMembership.objects.create(user=self.user, group=self.group, role='member')
        
    def test_send_notification_utility(self):
        """Test the send_notification utility."""
        success = send_notification(
            self.user,
            "Test Subject",
            "Test Message",
            notification_type='email'
        )
        
        self.assertTrue(success)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")
        
    def test_send_reminders_command(self):
        """Test the send_reminders management command."""
        # User hasn't contributed, so should receive reminder
        call_command('send_reminders')
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reminder: Contribution Due", mail.outbox[0].subject)
        self.assertIn("Test Group", mail.outbox[0].subject)
