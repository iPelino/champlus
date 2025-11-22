"""
Tests for async notifications.
"""

from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from notifications.models import Notification
from notifications.utils import send_notification
from notifications.tasks import send_email_task

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class AsyncNotificationTest(TestCase):
    """Test cases for async notifications."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="asyncuser",
            email="async@test.com",
            password="password"
        )
        
    def test_async_email_sending(self):
        """Test that email is sent via Celery task (eagerly)."""
        success = send_notification(
            self.user,
            "Async Subject",
            "Async Message",
            notification_type='email'
        )
        
        self.assertTrue(success)
        
        # Check notification status (should be sent because of eager execution)
        notification = Notification.objects.first()
        self.assertEqual(notification.status, 'sent')
        self.assertIsNotNone(notification.sent_at)
        
        # Check email outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Async Subject")
        
    def test_task_direct_execution(self):
        """Test executing the task directly."""
        notification = Notification.objects.create(
            recipient=self.user,
            subject="Direct Task",
            message="Message",
            notification_type='email'
        )
        
        result = send_email_task(notification.id)
        
        self.assertIn("Email sent", result)
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'sent')
        self.assertEqual(len(mail.outbox), 1)
