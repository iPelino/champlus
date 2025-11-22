from django.contrib import admin
from .models import Transaction, TransactionSplit


class TransactionSplitInline(admin.TabularInline):
    model = TransactionSplit
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'transaction_type', 'group', 'paid_by', 'transaction_date', 'created_at']
    list_filter = ['transaction_type', 'transaction_date', 'created_at']
    search_fields = ['description', 'group__name', 'paid_by__username', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TransactionSplitInline]
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('group', 'transaction_type', 'description', 'amount', 'transaction_date')
        }),
        ('User Info', {
            'fields': ('created_by', 'paid_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TransactionSplit)
class TransactionSplitAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'user', 'amount', 'is_settled', 'settled_at']
    list_filter = ['is_settled', 'settled_at']
    search_fields = ['transaction__description', 'user__username']
    readonly_fields = ['settled_at']
