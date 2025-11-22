from django.urls import path
from .views import InitiatePaymentView, StripeWebhookView, MTNCallbackView

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('callbacks/mtn/', MTNCallbackView.as_view(), name='mtn-callback'),
]
