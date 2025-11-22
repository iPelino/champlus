"""
Tests for tenant registration.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tenants.models import Tenant
from groups.models import Group
from members.models import UserProfile, GroupMembership

class RegistrationTest(TestCase):
    """Test cases for group/tenant registration."""
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register-group')
        self.valid_payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'securepassword123',
            'phone_number': '+254700000000',
            'group_name': 'My Chama',
            'subdomain': 'mychama'
        }
    
    def test_registration_success(self):
        """Test successful registration of a new group."""
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify User created
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
        user = User.objects.get(email='john@example.com')
        
        # Verify Tenant created
        self.assertTrue(Tenant.objects.filter(subdomain='mychama').exists())
        tenant = Tenant.objects.get(subdomain='mychama')
        
        # Verify Group created
        self.assertTrue(Group.objects.filter(tenant=tenant, name='My Chama').exists())
        group = Group.objects.get(tenant=tenant)
        
        # Verify UserProfile created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
        # Verify GroupMembership (Admin) created
        self.assertTrue(GroupMembership.objects.filter(
            user=user, 
            group=group, 
            role='admin'
        ).exists())
        
    def test_registration_duplicate_email(self):
        """Test registration with existing email fails."""
        # Create existing user
        User.objects.create_user(username='john@example.com', email='john@example.com', password='pw')
        
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_registration_duplicate_subdomain(self):
        """Test registration with existing subdomain fails."""
        # Create existing tenant
        Tenant.objects.create(name='Existing', slug='mychama', subdomain='mychama')
        
        response = self.client.post(self.url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('subdomain', response.data)
