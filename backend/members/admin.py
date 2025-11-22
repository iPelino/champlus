"""
Admin configuration for members app.
"""

from django.contrib import admin
from .models import UserProfile, GroupMembership, GroupInvitation


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    
    list_display = [
        'user',
        'phone_number',
        'timezone',
        'email_notifications',
        'created_at',
    ]
    
    list_filter = [
        'email_notifications',
        'sms_notifications',
        'created_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'phone_number',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    """Admin interface for GroupMembership model."""
    
    list_display = [
        'user',
        'group',
        'role',
        'is_active',
        'joined_at',
    ]
    
    list_filter = [
        'role',
        'is_active',
        'joined_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'group__name',
    ]
    
    readonly_fields = [
        'id',
        'joined_at',
        'updated_at',
    ]


@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    """Admin interface for GroupInvitation model."""
    
    list_display = [
        'email',
        'group',
        'invited_by',
        'role',
        'status',
        'created_at',
        'expires_at',
    ]
    
    list_filter = [
        'status',
        'role',
        'created_at',
    ]
    
    search_fields = [
        'email',
        'group__name',
        'invited_by__username',
    ]
    
    readonly_fields = [
        'id',
        'token',
        'created_at',
        'accepted_at',
    ]
