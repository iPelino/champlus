"""
Admin configuration for tenants app.
"""

from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""
    
    list_display = [
        'name',
        'subdomain',
        'subscription_status',
        'is_active',
        'created_at',
    ]
    
    list_filter = [
        'subscription_status',
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'subdomain',
        'slug',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'subdomain')
        }),
        ('Status', {
            'fields': ('is_active', 'subscription_status')
        }),
        ('Subscription', {
            'fields': ('trial_ends_at', 'subscription_ends_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Return all tenants for superadmin."""
        # Bypass tenant filtering in admin
        return super().get_queryset(request)
