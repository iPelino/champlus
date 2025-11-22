"""
Celery tasks for notifications.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification

@shared_task
def send_email_task(notification_id):
    """
    Async task to send an email.
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        send_mail(
            notification.subject,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [notification.recipient.email],
            fail_silently=False,
        )
        
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        return f"Email sent to {notification.recipient.email}"
        
    except Notification.DoesNotExist:
        return "Notification not found"
    except Exception as e:
        if 'notification' in locals():
            notification.status = 'failed'
            notification.save()
        return f"Failed to send email: {e}"
