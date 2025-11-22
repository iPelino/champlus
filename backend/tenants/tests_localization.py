"""
Tests for localization settings (currency and language).
"""

from django.test import TestCase
from tenants.models import Tenant
from groups.models import Group
from django.utils import timezone
from datetime import timedelta

class LocalizationTest(TestCase):
    """Test cases for localization settings."""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            subdomain="testtenant",
            slug="test-tenant",
            language='rw' # Test non-default language
        )
        
    def test_tenant_language(self):
        """Test tenant language setting."""
        self.assertEqual(self.tenant.language, 'rw')
        
        # Test default
        tenant2 = Tenant.objects.create(
            name="Default Lang Tenant",
            subdomain="defaultlang",
            slug="default-lang"
        )
        self.assertEqual(tenant2.language, 'en')
        
    def test_group_default_currency(self):
        """Test group default currency is RWF."""
        group = Group.objects.create(
            name="Test Group",
            tenant=self.tenant,
            contribution_amount=1000
        )
        
        self.assertEqual(group.currency, 'RWF')
