"""
Models for approval workflows.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import uuid

class ApprovalRequest(models.Model):
    """
    Represents a request that needs approval (Maker-Checker).
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # The object being acted upon (e.g., Loan, Expense)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100) # UUIDs are strings here
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Action details
    action_type = models.CharField(max_length=50, help_text=_("e.g., disburse_loan, create_expense"))
    data = models.JSONField(default=dict, blank=True, help_text=_("Data needed to execute the action"))
    
    # Actors
    requester = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='approval_requests'
    )
    reviewer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_requests'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, help_text=_("Reason for rejection"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.action_type} by {self.requester} ({self.status})"
