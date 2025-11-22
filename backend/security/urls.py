from django.urls import path
from .views import LoginWith2FAView, VerifyOTPView

urlpatterns = [
    path('login/', LoginWith2FAView.as_view(), name='login-2fa'),
    path('verify/', VerifyOTPView.as_view(), name='verify-2fa'),
]
