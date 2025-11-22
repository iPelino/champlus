"""
Utilities for 2FA.
"""

import random
import string
from django.core.cache import cache
from django.conf import settings
from notifications.utils import send_notification

def generate_otp(length=6):
    """Generate a numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp(user):
    """Generate and send OTP to user."""
    otp = generate_otp()
    cache_key = f"otp_{user.id}"
    cache.set(cache_key, otp, timeout=300) # 5 minutes
    
    subject = "Your Login Verification Code"
    message = f"Your verification code is: {otp}\n\nIt expires in 5 minutes."
    
    send_notification(user, subject, message, notification_type='email')
    return True

def verify_otp(user, otp):
    """Verify the OTP."""
    cache_key = f"otp_{user.id}"
    cached_otp = cache.get(cache_key)
    
    if cached_otp and cached_otp == otp:
        cache.delete(cache_key)
        return True
    return False
