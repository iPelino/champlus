"""
Password reset views.
"""

from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.utils.encoding import force_str

class PasswordResetRequestView(views.APIView):
    """
    Request password reset email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetForm(data=request.data)
        if serializer.is_valid():
            # This sends the email using Django's default mechanism
            # You need to configure EMAIL_BACKEND in settings.py
            serializer.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='tenants/password_reset_email.html'
            )
            return Response(
                {"message": "Password reset email sent if account exists."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(views.APIView):
    """
    Confirm password reset with token and new password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        password = request.data.get('password')

        if not (uidb64 and token and password):
            return Response(
                {"error": "Missing uidb64, token, or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid token or user ID."},
                status=status.HTTP_400_BAD_REQUEST
            )
