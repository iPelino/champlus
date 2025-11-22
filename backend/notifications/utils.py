"""
Utilities for sending notifications.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification
from .tasks import send_email_task

def send_notification(user, subject, message, notification_type='email'):
    """
    Send a notification to a user.
    """
    # Create notification record
    notification = Notification.objects.create(
        recipient=user,
        subject=subject,
        message=message,
        notification_type=notification_type,
        status='pending'
    )
    
    try:
        if notification_type == 'email':
            # Trigger async task
            send_email_task.delay(notification.id)
            
        elif notification_type == 'in_app':
            # Just save as pending/sent (in-app is "sent" immediately to DB)
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()
            
        # SMS logic would go here
        
        return True
        
    except Exception as e:
        notification.status = 'failed'
        notification.save()
        print(f"Failed to queue notification: {e}")
        return False
