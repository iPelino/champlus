"""
Models for the loans app.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Loan(models.Model):
    """
    Represents a loan taken by a member from the group.
    """
    
    STATUS_CHOICES = [
        ('requested', _('Requested')),
        ('approved', _('Approved')),
        ('active', _('Active (Disbursed)')),
        ('rejected', _('Rejected')),
        ('paid', _('Fully Paid')),
        ('defaulted', _('Defaulted')),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='loans'
    )
    
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Principal loan amount")
    )
    
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_("Interest rate in percentage (e.g., 10.00 for 10%)")
    )
    
    duration_months = models.PositiveIntegerField(
        help_text=_("Loan duration in months")
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested'
    )
    
    # Dates
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Approvals
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_loans'
    )
    
    # Calculated fields (denormalized for performance)
    total_amount_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    def calculate_total_payable(self):
        """Simple interest calculation: Principal + (Principal * Rate / 100)."""
        interest = self.amount * (self.interest_rate / Decimal('100'))
        return self.amount + interest
        
    def save(self, *args, **kwargs):
        if not self.total_amount_payable:
            self.total_amount_payable = self.calculate_total_payable()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.amount} to {self.borrower} ({self.status})"

class Repayment(models.Model):
    """
    Represents a repayment made towards a loan.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='repayments'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    paid_at = models.DateTimeField(auto_now_add=True)
    
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_repayments'
    )
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Repayment {self.amount} for {self.loan}"
