"""
Serializers for the members app.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GroupInvitation, GroupMembership, UserProfile

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone_number', 'timezone', 'language']

class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for GroupMembership model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'role', 'is_active', 'joined_at']

class GroupInvitationSerializer(serializers.ModelSerializer):
    """Serializer for creating and viewing invitations."""
    invited_by = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupInvitation
        fields = ['id', 'email', 'role', 'status', 'message', 'invited_by', 'created_at', 'expires_at']
        read_only_fields = ['status', 'invited_by', 'created_at', 'expires_at']

class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting an invitation."""
    token = serializers.UUIDField()
    password = serializers.CharField(required=False, write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
