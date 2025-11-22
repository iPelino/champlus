"""
Tests for security features.
"""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from security.models import AuditLog
from django.core.cache import cache
from django.core import mail

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SecurityTest(TestCase):
    """Test cases for security features."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="secureuser",
            email="secure@test.com",
            password="password"
        )
        
    def test_audit_logging(self):
        """Test that write operations are audited."""
        self.client.force_authenticate(user=self.user)
        
        # Perform a write operation (e.g., create a loan - assuming loans app is installed)
        # Or simpler: just hit a mock endpoint if we had one.
        # Let's use the 2FA login endpoint which is a POST, but it's unauthenticated usually.
        # AuditMiddleware only logs authenticated requests.
        # Let's try to hit a known authenticated endpoint, e.g., logout (if it exists) or just mock a view.
        # Since we don't have a simple generic create view handy without setup, let's rely on the middleware logic.
        # We can use the 'repayment-create' endpoint if we set up data, or just create a dummy request.
        
        # Let's manually invoke middleware for testing to avoid complex setup
        from security.middleware import AuditMiddleware
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/api/some-resource/', {'data': 'test'})
        request.user = self.user
        
        middleware = AuditMiddleware(lambda r: None) # Mock get_response
        
        # Mock response
        class MockResponse:
            status_code = 201
        middleware.get_response = lambda r: MockResponse()
        
        middleware(request)
        
        self.assertEqual(AuditLog.objects.count(), 1)
        log = AuditLog.objects.first()
        self.assertEqual(log.actor, self.user)
        self.assertEqual(log.action, 'create')
        
    def test_2fa_flow(self):
        """Test the 2FA login flow."""
        # Step 1: Login
        login_url = reverse('login-2fa')
        response = self.client.post(login_url, {
            'username': 'secureuser',
            'password': 'password'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)
        
        # Check OTP sent
        self.assertEqual(len(mail.outbox), 1)
        otp = cache.get(f"otp_{self.user.id}")
        self.assertIsNotNone(otp)
        
        # Step 2: Verify
        verify_url = reverse('verify-2fa')
        response = self.client.post(verify_url, {
            'user_id': self.user.id,
            'otp': otp
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
    def test_throttling(self):
        """Test rate limiting."""
        # We need to enable caching for throttling to work in tests
        # Using override_settings to ensure LocMemCache is used
        
        url = reverse('login-2fa')
        # Limit is 5/min
        for _ in range(5):
            self.client.post(url, {'username': 'wrong', 'password': 'wrong'})
            
        # 6th request should be throttled
        response = self.client.post(url, {'username': 'wrong', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
