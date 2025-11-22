"""
Views for the members app.
"""

from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from .models import GroupInvitation, GroupMembership, UserProfile
from .serializers import (
    GroupInvitationSerializer, 
    AcceptInvitationSerializer, 
    GroupMembershipSerializer
)
from tenants.middleware import get_current_tenant

class SendInvitationView(generics.CreateAPIView):
    """
    Send an invitation to join the group.
    """
    serializer_class = GroupInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Get current tenant and group
        # Assuming the user is an admin of the current group context
        # For now, we'll just use the user's active membership or similar logic
        # But wait, how do we know WHICH group?
        # In a multi-tenant app, the tenant is in the request.
        # But a tenant might have multiple groups? 
        # Based on models, Group is linked to Tenant.
        # If we assume 1 Group per Tenant for now (as per registration flow),
        # we can get the group from the tenant.
        
        tenant = self.request.tenant
        if not tenant:
            raise serializers.ValidationError("No active tenant found.")
            
        # Find the group for this tenant
        # This is a simplification. Ideally, the group ID should be in the URL or context.
        # Let's assume the first group for the tenant for now, or pass group_id.
        # Given the registration flow created one group per tenant.
        group = tenant.groups.first()
        if not group:
            raise serializers.ValidationError("No group found for this tenant.")
            
        # Check if user is admin of this group
        membership = GroupMembership.objects.filter(
            user=self.request.user, 
            group=group, 
            role='admin',
            is_active=True
        ).first()
        
        if not membership:
            raise permissions.PermissionDenied("You must be an admin to invite members.")
            
        # Set expiration (e.g., 7 days)
        expires_at = timezone.now() + timezone.timedelta(days=7)
        
        serializer.save(
            group=group,
            invited_by=self.request.user,
            expires_at=expires_at
        )
        
        # TODO: Send email here

class AcceptInvitationView(views.APIView):
    """
    Accept an invitation.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        password = serializer.validated_data.get('password')
        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')
        
        try:
            invitation = GroupInvitation.objects.get(token=token)
        except GroupInvitation.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_404_NOT_FOUND)
            
        if invitation.status != 'pending':
            return Response({"error": "Invitation is no longer valid."}, status=status.HTTP_400_BAD_REQUEST)
            
        if invitation.expires_at < timezone.now():
            invitation.status = 'expired'
            invitation.save()
            return Response({"error": "Invitation has expired."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if user already exists with this email
        user = User.objects.filter(email=invitation.email).first()
        
        with transaction.atomic():
            if not user:
                if not password:
                    return Response({"error": "Password is required for new users."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Create new user
                username = invitation.email.split('@')[0]
                # Ensure unique username
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{uuid.uuid4().hex[:4]}"
                    
                user = User.objects.create_user(
                    username=username,
                    email=invitation.email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create profile
                UserProfile.objects.create(user=user)
            
            # Create membership
            GroupMembership.objects.create(
                user=user,
                group=invitation.group,
                role=invitation.role
            )
            
            # Update invitation
            invitation.status = 'accepted'
            invitation.accepted_at = timezone.now()
            invitation.invited_user = user
            invitation.save()
            
        return Response({"message": "Invitation accepted successfully."}, status=status.HTTP_200_OK)

class MemberListView(generics.ListAPIView):
    """
    List members of the current group.
    """
    serializer_class = GroupMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        if not tenant:
            return GroupMembership.objects.none()
            
        group = tenant.groups.first()
        if not group:
            return GroupMembership.objects.none()
            
        # Check if requesting user is a member
        if not GroupMembership.objects.filter(user=self.request.user, group=group, is_active=True).exists():
            return GroupMembership.objects.none()
            
        return GroupMembership.objects.filter(group=group, is_active=True)
