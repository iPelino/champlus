"""
Admin configuration for groups app.
"""

from django.contrib import admin
from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin interface for Group model."""
    
    list_display = [
        'name',
        'tenant',
        'contribution_amount',
        'contribution_frequency',
        'currency',
        'is_active',
        'created_at',
    ]
    
    list_filter = [
        'is_active',
        'contribution_frequency',
        'currency',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'description',
        'tenant__name',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'tenant', 'name', 'description')
        }),
        ('Financial Settings', {
            'fields': (
                'contribution_amount',
                'contribution_frequency',
                'currency',
                'allow_variable_contributions',
            )
        }),
        ('Group Settings', {
            'fields': (
                'require_contribution_approval',
                'late_payment_grace_days',
                'is_active',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
