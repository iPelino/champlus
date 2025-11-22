"""
Tenancy middleware for multi-tenant data isolation.

This middleware identifies the current tenant based on the subdomain
and ensures all database queries are scoped to that tenant.
"""

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from tenants.models import Tenant
import threading

# Thread-local storage for current tenant
_thread_locals = threading.local()


def get_current_tenant():
    """Get the current tenant from thread-local storage."""
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage."""
    _thread_locals.tenant = tenant


def clear_current_tenant():
    """Clear the current tenant from thread-local storage."""
    if hasattr(_thread_locals, 'tenant'):
        delattr(_thread_locals, 'tenant')


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to identify and set the current tenant based on subdomain.
    
    This middleware:
    1. Extracts the subdomain from the request
    2. Looks up the tenant in the database
    3. Stores the tenant in thread-local storage
    4. Makes it available to all subsequent code in the request
    """
    
    def process_request(self, request):
        """
        Process incoming request to identify tenant.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            None if tenant is found and valid, HttpResponseForbidden otherwise
        """
        # Clear any existing tenant from previous request
        clear_current_tenant()
        
        # Get the host from the request
        host = request.get_host().split(':')[0]  # Remove port if present
        
        # Extract subdomain
        # Assuming format: subdomain.domain.com or subdomain.localhost
        parts = host.split('.')
        
        # Skip tenant resolution for localhost without subdomain (for development)
        if host == 'localhost' or host == '127.0.0.1' or host == 'testserver':
            # In development, you might want to use a default tenant
            # or allow access without tenant for admin/setup
            request.tenant = None
            return None
            
        # Skip tenant resolution for registration endpoint
        if request.path.startswith('/api/tenants/register/'):
            request.tenant = None
            return None
            
        # Skip tenant resolution for auth endpoints
        if request.path.startswith('/api/tenants/login/') or request.path.startswith('/api/tenants/logout/') or request.path.startswith('/api/tenants/password-reset/'):
            request.tenant = None
            return None

        # Skip tenant resolution for invitation acceptance (it's cross-tenant or public)
        if request.path.startswith('/api/members/invitations/accept/'):
            request.tenant = None
            return None

        # Skip tenant resolution for billing webhook
        if request.path.startswith('/api/tenants/billing/webhook/'):
            request.tenant = None
            return None
        
        # For development with subdomain.localhost or subdomain.testserver
        if len(parts) >= 2 and (parts[-1] == 'localhost' or parts[-1] == 'testserver'):
            subdomain = parts[0]
        # For production with subdomain.domain.com
        elif len(parts) >= 3:
            subdomain = parts[0]
        else:
            # No subdomain found
            return HttpResponseForbidden("Invalid domain. Please access via your organization's subdomain.")
        
        # Skip tenant resolution for 'www' subdomain
        if subdomain == 'www':
            return HttpResponseForbidden("Please access via your organization's subdomain.")
        
        # Look up the tenant
        try:
            tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
            
            # Check if tenant subscription is active
            if not tenant.is_subscription_active():
                return HttpResponseForbidden(
                    "Your subscription is not active. Please contact support or renew your subscription."
                )
            
            # Set the tenant in thread-local storage
            set_current_tenant(tenant)
            
            # Also attach to request for easy access
            request.tenant = tenant
            
        except Tenant.DoesNotExist:
            return HttpResponseForbidden(
                f"Organization '{subdomain}' not found. Please check your URL or contact support."
            )
        
        return None
    
    def process_response(self, request, response):
        """
        Clean up tenant from thread-local storage after request.
        
        Args:
            request: Django HttpRequest object
            response: Django HttpResponse object
            
        Returns:
            The response object
        """
        clear_current_tenant()
        return response
    
    def process_exception(self, request, exception):
        """
        Clean up tenant from thread-local storage on exception.
        
        Args:
            request: Django HttpRequest object
            exception: The exception that was raised
            
        Returns:
            None (allows exception to propagate)
        """
        clear_current_tenant()
        return None
