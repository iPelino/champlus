"""
Middleware for security auditing.
"""

from .models import AuditLog
import json

class AuditMiddleware:
    """
    Middleware to log write operations (POST, PUT, PATCH, DELETE).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only log authenticated write requests
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Determine action
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete'
            }
            
            # Try to get resource info from URL or view
            # This is a simplified approach; robust auditing often uses Signals or Mixins
            resource_type = "Unknown"
            if request.resolver_match:
                # e.g., 'financials.views.TransactionViewSet' -> 'Transaction'
                # Or just use the URL path
                resource_type = request.path[:50]
            
            # Capture details
            details = {}
            if request.method in ['POST', 'PUT', 'PATCH']:
                # Be careful not to log passwords or sensitive data
                # For now, we'll just log that data was sent, or specific safe fields
                pass
                
            AuditLog.objects.create(
                actor=request.user,
                action=action_map.get(request.method, 'unknown'),
                resource_type=resource_type,
                ip_address=self.get_client_ip(request),
                details={'status_code': response.status_code}
            )
            
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
