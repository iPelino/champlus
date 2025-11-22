from rest_framework import views, status, permissions
from rest_framework.response import Response
from .models import ApprovalRequest
from .service import ApprovalService
from .serializers import ApprovalRequestSerializer

class ApprovalListView(views.APIView):
    """
    List pending approvals for the user's group(s).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Filter requests where user is an admin of the group
        # Simplified: just show all for now, or filter by tenant
        # In real app: Filter by groups where user.role == 'admin'
        
        requests = ApprovalRequest.objects.filter(status='pending')
        serializer = ApprovalRequestSerializer(requests, many=True)
        return Response(serializer.data)

class ApprovalActionView(views.APIView):
    """
    Approve or Reject a request.
    """
    permission_classes = [permissions.IsAuthenticated] # Should be IsAdminUser or GroupAdmin
    
    def post(self, request, pk, action):
        if action == 'approve':
            success, message = ApprovalService.approve_request(pk, request.user)
        elif action == 'reject':
            reason = request.data.get('reason', '')
            success, message = ApprovalService.reject_request(pk, request.user, reason)
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
            
        if success:
            return Response({"message": message})
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
