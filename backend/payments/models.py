"""
Models for payment tracking.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class PaymentTransaction(models.Model):
    """
    Represents a payment attempt (external transaction).
    Links to the internal financial Transaction if successful.
    """
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('mtn', 'MTN Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('pending_approval', _('Pending Approval')), # For manual verification
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Link to internal transaction (optional until success)
    internal_transaction = models.OneToOneField(
        'financials.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_details'
    )
    
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_transaction_id = models.CharField(max_length=255, blank=True, help_text=_("External ID (e.g., Stripe PI ID)"))
    
    # Proof of Payment for manual transfers
    proof_of_payment = models.FileField(upload_to='proofs/', null=True, blank=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='RWF')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.provider} {self.amount} {self.currency} - {self.status}"
