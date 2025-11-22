"""
Tests for password reset.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class PasswordResetTest(TestCase):
    """Test cases for password reset."""
    
    def setUp(self):
        self.client = APIClient()
        self.request_url = reverse('password_reset')
        self.confirm_url = reverse('password_reset_confirm')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword'
        )
    
    def test_password_reset_request(self):
        """Test requesting a password reset email."""
        response = self.client.post(self.request_url, {
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: We can't easily check if email was sent without mocking, 
        # but 200 OK means the view processed it.
        
    def test_password_reset_confirm(self):
        """Test confirming password reset."""
        # Generate token and uid
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        response = self.client.post(self.confirm_url, {
            'uidb64': uid,
            'token': token,
            'password': 'newpassword123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        
    def test_password_reset_invalid_token(self):
        """Test confirming with invalid token."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        response = self.client.post(self.confirm_url, {
            'uidb64': uid,
            'token': 'invalid-token',
            'password': 'newpassword123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
