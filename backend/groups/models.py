"""
Group models for managing financial groups within a tenant.

A tenant can have multiple groups (e.g., different chamas/savings groups).
This module defines the Group model and related settings.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from tenants.managers import TenantManager
import uuid


class Group(models.Model):
    """
    Represents a financial group (chama) within a tenant.
    
    A group is a collection of members who contribute and manage finances together.
    Each group belongs to a tenant and has its own settings and financial rules.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the group")
    )
    
    # Tenant relationship - each group belongs to one tenant
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='groups',
        help_text=_("The tenant this group belongs to")
    )
    
    # Group identification
    name = models.CharField(
        max_length=255,
        help_text=_("Name of the group")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Description of the group's purpose and goals")
    )
    
    # Financial settings
    contribution_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Standard contribution amount per member per period")
    )
    
    contribution_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
            ('biweekly', _('Bi-weekly')),
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('annual', _('Annual')),
        ],
        default='monthly',
        help_text=_("How often members should contribute")
    )
    
    currency = models.CharField(
        max_length=3,
        default='RWF',
        help_text=_("Currency code (ISO 4217, e.g., RWF, USD)")
    )
    
    # Group settings
    allow_variable_contributions = models.BooleanField(
        default=False,
        help_text=_("Allow members to contribute amounts different from the standard")
    )
    
    require_contribution_approval = models.BooleanField(
        default=False,
        help_text=_("Require admin approval for contribution entries")
    )
    
    late_payment_grace_days = models.PositiveIntegerField(
        default=7,
        help_text=_("Number of days grace period before marking as defaulter")
    )
    
    # Group status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this group is currently active")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this group was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this group was last updated")
    )
    
    # Use TenantManager for automatic tenant filtering
    objects = TenantManager()
    
    class Meta:
        db_table = 'groups'
        ordering = ['-created_at']
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['created_at']),
        ]
        # Ensure group names are unique within a tenant
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='unique_group_name_per_tenant'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tenant.name})"
