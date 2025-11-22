"""
Authentication views.
"""

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(TokenObtainPairView):
    """
    Login view that returns JWT tokens.
    Uses default TokenObtainPairView implementation.
    """
    pass

class LogoutView(views.APIView):
    """
    Logout view that blacklists the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
