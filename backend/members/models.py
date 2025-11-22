"""
Member models for managing users and their group memberships.

This module defines user profiles, group memberships, and invitation models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
import uuid


class UserProfile(models.Model):
    """
    Extended user profile linked to Django's User model.
    
    Stores additional user information beyond Django's default User model.
    Each user can be a member of multiple groups across multiple tenants.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the user profile")
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text=_("Associated Django user account")
    )
    
    # Contact information
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Phone number for notifications")
    )
    
    # Profile settings
    timezone = models.CharField(
        max_length=50,
        default='Africa/Nairobi',
        help_text=_("User's timezone")
    )
    
    language = models.CharField(
        max_length=10,
        default='en',
        help_text=_("Preferred language code")
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text=_("Receive email notifications")
    )
    
    sms_notifications = models.BooleanField(
        default=False,
        help_text=_("Receive SMS notifications")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this profile was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this profile was last updated")
    )
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class GroupMembership(models.Model):
    """
    Represents a user's membership in a specific group.
    
    Links users to groups with role-based permissions.
    """
    
    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('treasurer', _('Treasurer')),
        ('member', _('Member')),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the membership")
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_memberships',
        help_text=_("The user who is a member")
    )
    
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text=_("The group the user belongs to")
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        help_text=_("User's role in the group")
    )
    
    # Membership status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this membership is currently active")
    )
    
    # Timestamps
    joined_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the user joined the group")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When this membership was last updated")
    )
    
    class Meta:
        db_table = 'group_memberships'
        ordering = ['-joined_at']
        verbose_name = _('Group Membership')
        verbose_name_plural = _('Group Memberships')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['group', 'is_active']),
        ]
        # Ensure a user can only have one membership per group
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                name='unique_user_per_group'
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class GroupInvitation(models.Model):
    """
    Represents an invitation to join a group.
    
    Allows group admins to invite new members via email.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('declined', _('Declined')),
        ('expired', _('Expired')),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the invitation")
    )
    
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text=_("The group the invitation is for")
    )
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        help_text=_("User who sent the invitation")
    )
    
    # Invitee information
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text=_("Email address of the invitee")
    )
    
    invited_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_invitations',
        help_text=_("User account if invitee already has one")
    )
    
    # Invitation details
    role = models.CharField(
        max_length=20,
        choices=GroupMembership.ROLE_CHOICES,
        default='member',
        help_text=_("Role to assign when invitation is accepted")
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Current status of the invitation")
    )
    
    message = models.TextField(
        blank=True,
        help_text=_("Optional message from the inviter")
    )
    
    # Security token for invitation link
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_("Unique token for the invitation link")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the invitation was sent")
    )
    
    expires_at = models.DateTimeField(
        help_text=_("When the invitation expires")
    )
    
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the invitation was accepted")
    )
    
    class Meta:
        db_table = 'group_invitations'
        ordering = ['-created_at']
        verbose_name = _('Group Invitation')
        verbose_name_plural = _('Group Invitations')
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['token']),
            models.Index(fields=['group', 'status']),
        ]
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.group.name}"
