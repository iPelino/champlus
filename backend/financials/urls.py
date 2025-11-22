"""
URL configuration for the financials app.
"""

from django.urls import path
from .views import (
    ContributionListCreateView, 
    ExpenseListCreateView, 
    LedgerView,
    MemberDashboardView,
    DefaulterListView,
    StatementExportView
)

urlpatterns = [
    path('contributions/', ContributionListCreateView.as_view(), name='contribution-list'),
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list'),
    path('ledger/', LedgerView.as_view(), name='ledger'),
    path('dashboard/', MemberDashboardView.as_view(), name='member-dashboard'),
    path('defaulters/', DefaulterListView.as_view(), name='defaulter-list'),
    path('statement/export/', StatementExportView.as_view(), name='statement-export'),
]
