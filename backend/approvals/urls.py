from django.urls import path
from .views import ApprovalListView, ApprovalActionView

urlpatterns = [
    path('', ApprovalListView.as_view(), name='approval-list'),
    path('<uuid:pk>/<str:action>/', ApprovalActionView.as_view(), name='approval-action'),
]
