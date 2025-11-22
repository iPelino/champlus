"""
Middleware for handling tenant-specific language settings.
"""

from django.utils import translation
from django.conf import settings

class TenantLanguageMiddleware:
    """
    Middleware to activate the tenant's preferred language.
    
    This should run after TenantMiddleware so that request.tenant is available.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Activate tenant language if available
        if hasattr(request, 'tenant') and request.tenant:
            language = request.tenant.language
            if language:
                translation.activate(language)
                request.LANGUAGE_CODE = translation.get_language()
        
        response = self.get_response(request)
        
        # Deactivate translation to avoid leaking into other requests
        translation.deactivate()
        
        return response
