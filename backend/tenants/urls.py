from django.urls import path
from .views import RegisterGroupView
from .views_auth import LoginView, LogoutView
from .views_password import PasswordResetRequestView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenRefreshView
from .views_billing import (
    SubscriptionStatusView,
    CreateCheckoutSessionView,
    BillingPortalView,
    MockWebhookView
)

urlpatterns = [
    path('register/', RegisterGroupView.as_view(), name='register-group'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Billing
    path('billing/status/', SubscriptionStatusView.as_view(), name='subscription-status'),
    path('billing/checkout/', CreateCheckoutSessionView.as_view(), name='create-checkout'),
    path('billing/portal/', BillingPortalView.as_view(), name='billing-portal'),
    path('billing/webhook/', MockWebhookView.as_view(), name='mock-webhook'),
]
