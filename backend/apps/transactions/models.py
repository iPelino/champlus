from django.db import models
from django.conf import settings
from decimal import Decimal


class Transaction(models.Model):
    """
    Model representing a transaction/expense in a group.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('expense', 'Expense'),
        ('payment', 'Payment'),
    ]

    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_transactions'
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        default='expense'
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: Track who paid and who owes
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paid_transactions',
        help_text='User who paid for this transaction'
    )
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.description} - ${self.amount} ({self.transaction_type})"


class TransactionSplit(models.Model):
    """
    Model representing how a transaction is split among group members.
    """
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='splits'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transaction_splits'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'transaction_splits'
        unique_together = ['transaction', 'user']

    def __str__(self):
        status = "Settled" if self.is_settled else "Pending"
        return f"{self.user.username} owes ${self.amount} for {self.transaction.description} ({status})"
