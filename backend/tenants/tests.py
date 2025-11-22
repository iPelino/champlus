"""
Tests for tenant isolation and middleware.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from tenants.models import Tenant
from tenants.middleware import TenantMiddleware, get_current_tenant, set_current_tenant
from groups.models import Group
from datetime import datetime, timedelta


class TenantMiddlewareTest(TestCase):
    """Test cases for TenantMiddleware."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda request: None)
        
        # Create test tenants
        self.tenant1 = Tenant.objects.create(
            name="Tenant 1",
            slug="tenant-1",
            subdomain="tenant1",
            subscription_status="active",
            is_active=True
        )
        
        self.tenant2 = Tenant.objects.create(
            name="Tenant 2",
            slug="tenant-2",
            subdomain="tenant2",
            subscription_status="active",
            is_active=True
        )
    
    def test_tenant_identified_from_subdomain(self):
        """Test that middleware correctly identifies tenant from subdomain."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'tenant1.localhost'
        
        response = self.middleware.process_request(request)
        
        self.assertIsNone(response)  # No error response
        self.assertEqual(request.tenant, self.tenant1)
        self.assertEqual(get_current_tenant(), self.tenant1)
    
    def test_invalid_subdomain_returns_forbidden(self):
        """Test that invalid subdomain returns 403."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'nonexistent.localhost'
        
        response = self.middleware.process_request(request)
        
        self.assertEqual(response.status_code, 403)
    
    def test_inactive_tenant_returns_forbidden(self):
        """Test that inactive tenant returns 403."""
        self.tenant1.is_active = False
        self.tenant1.save()
        
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'tenant1.localhost'
        
        response = self.middleware.process_request(request)
        
        self.assertEqual(response.status_code, 403)


class TenantIsolationTest(TestCase):
    """Test cases for tenant data isolation."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenants
        self.tenant1 = Tenant.objects.create(
            name="Tenant 1",
            slug="tenant-1",
            subdomain="tenant1",
            subscription_status="active",
            is_active=True
        )
        
        self.tenant2 = Tenant.objects.create(
            name="Tenant 2",
            slug="tenant-2",
            subdomain="tenant2",
            subscription_status="active",
            is_active=True
        )
        
        # Create groups for each tenant
        self.group1 = Group.objects.create(
            tenant=self.tenant1,
            name="Group 1",
            contribution_amount=1000,
            contribution_frequency="monthly",
            currency="KES"
        )
        
        self.group2 = Group.objects.create(
            tenant=self.tenant2,
            name="Group 2",
            contribution_amount=2000,
            contribution_frequency="weekly",
            currency="USD"
        )
    
    def test_tenant_isolation_in_queries(self):
        """Test that queries are isolated by tenant."""
        # Set current tenant to tenant1
        set_current_tenant(self.tenant1)
        
        # Query should only return groups for tenant1
        groups = Group.objects.all()
        self.assertEqual(groups.count(), 1)
        self.assertEqual(groups.first(), self.group1)
        
        # Switch to tenant2
        set_current_tenant(self.tenant2)
        
        # Query should only return groups for tenant2
        groups = Group.objects.all()
        self.assertEqual(groups.count(), 1)
        self.assertEqual(groups.first(), self.group2)
    
    def test_cross_tenant_access_prevented(self):
        """Test that cross-tenant access is prevented."""
        # Set current tenant to tenant1
        set_current_tenant(self.tenant1)
        
        # Try to access group from tenant2 by ID
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(id=self.group2.id)
