"""
Tests for authentication.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class AuthTest(TestCase):
    """Test cases for authentication."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.logout_url = reverse('auth_logout')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_logout_success(self):
        """Test successful logout (token blacklisting)."""
        # Get tokens first
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Logout
        response = self.client.post(self.logout_url, {
            'refresh': str(refresh)
        })
        
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        
        # Verify token is blacklisted
        with self.assertRaises(Exception):
            refresh.check_blacklist()
            
    def test_logout_without_token(self):
        """Test logout without authentication fails."""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
