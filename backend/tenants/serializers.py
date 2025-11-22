"""
Serializers for tenant and group registration.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from tenants.models import Tenant
from groups.models import Group
from members.models import UserProfile, GroupMembership
from datetime import datetime, timedelta
from django.utils import timezone

class GroupAdminRegistrationSerializer(serializers.Serializer):
    """
    Serializer for registering a new group admin, tenant, and initial group.
    
    This handles the full onboarding flow:
    1. Create User
    2. Create Tenant
    3. Create Group
    4. Create UserProfile
    5. Assign User as Group Admin
    """
    
    # User fields
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    phone_number = serializers.CharField(max_length=20, required=False)
    
    # Tenant/Group fields
    group_name = serializers.CharField(max_length=255)
    subdomain = serializers.SlugField(max_length=63)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
        
    def validate_subdomain(self, value):
        if Tenant.objects.filter(subdomain=value).exists():
            raise serializers.ValidationError("This subdomain is already taken.")
        return value

    def create(self, validated_data):
        with transaction.atomic():
            # 1. Create User
            user = User.objects.create_user(
                username=validated_data['email'],  # Use email as username
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name']
            )
            
            # 2. Create Tenant
            # Default to 14-day trial
            trial_end = timezone.now() + timedelta(days=14)
            
            tenant = Tenant.objects.create(
                name=validated_data['group_name'], # Use group name as tenant name initially
                slug=validated_data['subdomain'],
                subdomain=validated_data['subdomain'],
                subscription_status='trial',
                trial_ends_at=trial_end,
                is_active=True
            )
            
            # 3. Create Group
            # We need to temporarily set the current tenant context or manually assign it
            # Since we are in a atomic block and this might be a public endpoint, 
            # we manually assign the tenant.
            group = Group.objects.create(
                tenant=tenant,
                name=validated_data['group_name'],
                contribution_amount=0, # Default, can be updated later
                contribution_frequency='monthly'
            )
            
            # 4. Create UserProfile
            UserProfile.objects.create(
                user=user,
                phone_number=validated_data.get('phone_number', '')
            )
            
            # 5. Create GroupMembership (Admin)
            GroupMembership.objects.create(
                user=user,
                group=group,
                role='admin',
                is_active=True
            )
            
            return {
                'user': user,
                'tenant': tenant,
                'group': group
            }
