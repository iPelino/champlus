"""
Admin configuration for financials app.
"""

from django.contrib import admin
from .models import Contribution, Expense, Transaction


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    """Admin interface for Contribution model."""
    
    list_display = [
        'member',
        'group',
        'amount',
        'contribution_date',
        'payment_method',
        'status',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'contribution_date',
        'created_at',
    ]
    
    search_fields = [
        'member__username',
        'group__name',
        'reference_number',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'group', 'member')
        }),
        ('Financial Details', {
            'fields': (
                'amount',
                'payment_method',
                'reference_number',
            )
        }),
        ('Period', {
            'fields': (
                'contribution_date',
                'period_start',
                'period_end',
            )
        }),
        ('Approval', {
            'fields': (
                'status',
                'recorded_by',
                'approved_by',
                'approved_at',
            )
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Admin interface for Expense model."""
    
    list_display = [
        'description',
        'group',
        'amount',
        'category',
        'expense_date',
        'status',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'category',
        'expense_date',
        'created_at',
    ]
    
    search_fields = [
        'description',
        'group__name',
        'payment_reference',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'group', 'description', 'category')
        }),
        ('Financial Details', {
            'fields': (
                'amount',
                'expense_date',
                'beneficiary',
            )
        }),
        ('Approval Workflow', {
            'fields': (
                'status',
                'requested_by',
                'approved_by',
                'approved_at',
            )
        }),
        ('Payment Tracking', {
            'fields': (
                'paid_by',
                'paid_at',
                'payment_reference',
            )
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    
    list_display = [
        'transaction_type',
        'group',
        'amount',
        'balance_after',
        'transaction_date',
        'created_at',
    ]
    
    list_filter = [
        'transaction_type',
        'transaction_date',
        'created_at',
    ]
    
    search_fields = [
        'description',
        'group__name',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'group', 'transaction_type')
        }),
        ('Financial Details', {
            'fields': (
                'amount',
                'balance_after',
                'transaction_date',
                'description',
            )
        }),
        ('Related Records', {
            'fields': (
                'contribution',
                'expense',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'created_at',
            )
        }),
    )
