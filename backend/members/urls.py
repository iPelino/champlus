"""
URL configuration for the members app.
"""

from django.urls import path
from .views import SendInvitationView, AcceptInvitationView, MemberListView

urlpatterns = [
    path('invitations/send/', SendInvitationView.as_view(), name='send-invitation'),
    path('invitations/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('list/', MemberListView.as_view(), name='member-list'),
]
