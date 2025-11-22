"""
Tests for internationalization (i18n).
"""

from django.test import TestCase, RequestFactory
from django.utils import translation
from tenants.models import Tenant
from tenants.middleware import TenantMiddleware
from tenants.middleware_i18n import TenantLanguageMiddleware

class I18nTest(TestCase):
    """Test cases for internationalization."""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create tenants with different languages
        self.tenant_en = Tenant.objects.create(
            name="English Tenant",
            subdomain="english",
            slug="english-tenant",
            language='en'
        )
        
        self.tenant_rw = Tenant.objects.create(
            name="Kinyarwanda Tenant",
            subdomain="kinyarwanda",
            slug="rw-tenant",
            language='rw'
        )
        
    def test_tenant_language_activation(self):
        """Test that tenant language is activated by middleware."""
        
        # Test English Tenant
        request_en = self.factory.get('/', HTTP_HOST='english.testserver')
        
        # Simulate middleware chain
        tenant_middleware = TenantMiddleware(lambda r: None)
        tenant_middleware.process_request(request_en)
        
        i18n_middleware = TenantLanguageMiddleware(lambda r: None)
        i18n_middleware(request_en)
        
        self.assertEqual(request_en.LANGUAGE_CODE, 'en')
        
        # Test Kinyarwanda Tenant
        request_rw = self.factory.get('/', HTTP_HOST='kinyarwanda.testserver')
        
        tenant_middleware.process_request(request_rw)
        i18n_middleware(request_rw)
        
        self.assertEqual(request_rw.LANGUAGE_CODE, 'rw')
