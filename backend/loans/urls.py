from django.urls import path
from .views import LoanListCreateView, LoanDetailView, LoanActionView, RepaymentCreateView

urlpatterns = [
    path('', LoanListCreateView.as_view(), name='loan-list'),
    path('<uuid:pk>/', LoanDetailView.as_view(), name='loan-detail'),
    path('<uuid:pk>/<str:action>/', LoanActionView.as_view(), name='loan-action'),
    path('repay/', RepaymentCreateView.as_view(), name='repayment-create'),
]
