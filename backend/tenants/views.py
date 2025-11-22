"""
Views for tenant and group registration.
"""

from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import GroupAdminRegistrationSerializer

class RegisterGroupView(views.APIView):
    """
    API endpoint for registering a new group/tenant.
    
    Public endpoint that creates a new tenant, group, and admin user.
    """
    permission_classes = [AllowAny]
    serializer_class = GroupAdminRegistrationSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            
            return Response({
                'message': 'Registration successful',
                'tenant_id': result['tenant'].id,
                'subdomain': result['tenant'].subdomain,
                'admin_email': result['user'].email
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
