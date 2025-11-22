"""
Financial models for tracking contributions, expenses, and transactions.

This module defines the core financial tracking models for the ChamPlus platform.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Contribution(models.Model):
    """
    Represents a member's financial contribution to the group.
    
    Tracks individual contributions with amounts, dates, and approval status.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Cash')),
        ('mpesa', _('M-Pesa')),
        ('bank_transfer', _('Bank Transfer')),
        ('cheque', _('Cheque')),
        ('other', _('Other')),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the contribution")
    )
    
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='contributions',
        help_text=_("The group this contribution is for")
    )
    
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contributions',
        help_text=_("The member who made the contribution")
    )
    
    # Financial details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Contribution amount")
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        help_text=_("Method of payment")
    )
    
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Payment reference number (e.g., M-Pesa code)")
    )
    
    # Contribution period tracking
    contribution_date = models.DateField(
        help_text=_("Date when the contribution was made")
    )
    
    period_start = models.DateField(
        help_text=_("Start date of the contribution period")
    )
    
    period_end = models.DateField(
        help_text=_("End date of the contribution period")
    )
    
    # Approval workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='approved',  # Auto-approve by default, configurable per group
        help_text=_("Approval status of the contribution")
    )
    
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_contributions',
        help_text=_("User who recorded this contribution")
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_contributions',
        help_text=_("User who approved this contribution")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the contribution was approved")
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about this contribution")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this record was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this record was last updated")
    )
    
    class Meta:
        db_table = 'contributions'
        ordering = ['-contribution_date', '-created_at']
        verbose_name = _('Contribution')
        verbose_name_plural = _('Contributions')
        indexes = [
            models.Index(fields=['group', 'contribution_date']),
            models.Index(fields=['member', 'contribution_date']),
            models.Index(fields=['status']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.member.username} - {self.amount} ({self.contribution_date})"


class Expense(models.Model):
    """
    Represents a group expense or withdrawal.
    
    Tracks money spent from the group's funds.
    """
    
    CATEGORY_CHOICES = [
        ('loan', _('Member Loan')),
        ('welfare', _('Welfare/Emergency')),
        ('administrative', _('Administrative')),
        ('investment', _('Investment')),
        ('event', _('Event/Meeting')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the expense")
    )
    
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='expenses',
        help_text=_("The group this expense is for")
    )
    
    # Expense details
    description = models.CharField(
        max_length=255,
        help_text=_("Description of the expense")
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text=_("Category of expense")
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Expense amount")
    )
    
    expense_date = models.DateField(
        help_text=_("Date when the expense occurred")
    )
    
    # Beneficiary (if applicable, e.g., for loans)
    beneficiary = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_expenses',
        help_text=_("Member who received the funds (for loans, etc.)")
    )
    
    # Approval workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Approval status of the expense")
    )
    
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requested_expenses',
        help_text=_("User who requested/recorded this expense")
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses',
        help_text=_("User who approved this expense")
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the expense was approved")
    )
    
    # Payment tracking
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paid_expenses',
        help_text=_("User who marked this as paid")
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the expense was paid")
    )
    
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Payment reference number")
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about this expense")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this record was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this record was last updated")
    )
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date', '-created_at']
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        indexes = [
            models.Index(fields=['group', 'expense_date']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.description} - {self.amount} ({self.expense_date})"


class Transaction(models.Model):
    """
    Unified transaction ledger for all financial activities.
    
    This model provides a complete audit trail of all financial movements
    in the group, whether contributions or expenses.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('contribution', _('Contribution')),
        ('expense', _('Expense')),
        ('adjustment', _('Adjustment')),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the transaction")
    )
    
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text=_("The group this transaction belongs to")
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text=_("Type of transaction")
    )
    
    # Link to source record
    contribution = models.ForeignKey(
        Contribution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions',
        help_text=_("Related contribution if applicable")
    )
    
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions',
        help_text=_("Related expense if applicable")
    )
    
    # Transaction details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Transaction amount (positive for contributions, negative for expenses)")
    )
    
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Group balance after this transaction")
    )
    
    transaction_date = models.DateField(
        help_text=_("Date of the transaction")
    )
    
    description = models.CharField(
        max_length=255,
        help_text=_("Description of the transaction")
    )
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_transactions',
        help_text=_("User who created this transaction")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this transaction was recorded")
    )
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date', '-created_at']
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        indexes = [
            models.Index(fields=['group', 'transaction_date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['-transaction_date', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.transaction_date})"
