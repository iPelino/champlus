"""
Tenant models for multi-tenancy support.

This module defines the Tenant model which represents an isolated organization/group
in the multi-tenant architecture. Each tenant has its own isolated data space.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Tenant(models.Model):
    """
    Represents a tenant (organization/group) in the multi-tenant system.
    
    Each tenant is completely isolated from other tenants. All tenant-specific
    data should reference this model to ensure proper data isolation.
    """
    
    # Use UUID as primary key for better security and distribution
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the tenant")
    )
    
    # Tenant identification
    name = models.CharField(
        max_length=255,
        help_text=_("Display name of the tenant organization")
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text=_("URL-safe identifier for the tenant (e.g., 'acme-corp')")
    )
    
    # Subdomain for tenant isolation (e.g., acme.champlus.com)
    subdomain = models.CharField(
        max_length=63,  # DNS subdomain max length
        unique=True,
        db_index=True,
        help_text=_("Subdomain for this tenant (e.g., 'acme')")
    )
    
    # Tenant status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this tenant is active and can access the system")
    )
    
    # Subscription information
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', _('Trial')),
            ('active', _('Active')),
            ('suspended', _('Suspended')),
            ('cancelled', _('Cancelled')),
        ],
        default='trial',
        help_text=_("Current subscription status")
    )
    
    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the trial period ends")
    )
    
    subscription_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the current subscription period ends")
    )
    
    # Settings
    language = models.CharField(
        max_length=10,
        default='en',
        help_text=_("Default language for the tenant")
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this tenant was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this tenant was last updated")
    )
    
    class Meta:
        db_table = 'tenants'
        ordering = ['-created_at']
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'subscription_status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.subdomain})"
    
    def is_subscription_active(self):
        """Check if the tenant has an active subscription."""
        return self.subscription_status in ['trial', 'active'] and self.is_active
