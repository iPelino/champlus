"""
Models for the notifications app.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid

class Notification(models.Model):
    """
    Represents a notification sent to a user.
    """
    
    TYPE_CHOICES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('in_app', _('In-App')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('read', _('Read')), # For in-app
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='in_app'
    )
    
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.notification_type} to {self.recipient}: {self.subject}"
