"""
Views for the financials app.
"""

from rest_framework import generics, permissions, serializers, views, status
from rest_framework.response import Response
from django.db import transaction, models
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Contribution, Expense, Transaction
from .serializers import ContributionSerializer, ExpenseSerializer, TransactionSerializer
from members.models import GroupMembership
from members.serializers import UserSerializer

class ContributionListCreateView(generics.ListCreateAPIView):
    """
    List and create contributions.
    """
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        if not tenant:
            return Contribution.objects.none()
        group = tenant.groups.first()
        if not group:
            return Contribution.objects.none()
        return Contribution.objects.filter(group=group).order_by('-contribution_date')
        
    def perform_create(self, serializer):
        tenant = self.request.tenant
        if not tenant:
            raise serializers.ValidationError("No active tenant found.")
        group = tenant.groups.first()
        if not group:
            raise serializers.ValidationError("No group found.")
            
        # Determine member
        member_id = self.request.data.get('member_id')
        if member_id:
            # Verify member belongs to group (TODO)
            pass
        else:
            member = self.request.user
            
        with transaction.atomic():
            contribution = serializer.save(
                group=group,
                member=self.request.user, # Default to self for now if not specified
                recorded_by=self.request.user,
                status='approved' # Auto-approve for MVP
            )
            
            # Create Ledger Entry
            # Calculate new balance (simplified: sum of all transactions + this one)
            # Ideally we store current balance in Group model or calculate efficiently
            last_transaction = Transaction.objects.filter(group=group).order_by('-created_at').first()
            current_balance = last_transaction.balance_after if last_transaction else 0
            new_balance = current_balance + contribution.amount
            
            Transaction.objects.create(
                group=group,
                transaction_type='contribution',
                contribution=contribution,
                amount=contribution.amount,
                balance_after=new_balance,
                transaction_date=contribution.contribution_date,
                description=f"Contribution from {contribution.member.username}",
                created_by=self.request.user
            )

class ExpenseListCreateView(generics.ListCreateAPIView):
    """
    List and create expenses.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        if not tenant:
            return Expense.objects.none()
        group = tenant.groups.first()
        if not group:
            return Expense.objects.none()
        return Expense.objects.filter(group=group).order_by('-expense_date')
        
    def perform_create(self, serializer):
        tenant = self.request.tenant
        if not tenant:
            raise serializers.ValidationError("No active tenant found.")
        group = tenant.groups.first()
        if not group:
            raise serializers.ValidationError("No group found.")
            
        with transaction.atomic():
            expense = serializer.save(
                group=group,
                requested_by=self.request.user,
                status='approved' # Auto-approve for MVP
            )
            
            # Create Ledger Entry
            last_transaction = Transaction.objects.filter(group=group).order_by('-created_at').first()
            current_balance = last_transaction.balance_after if last_transaction else 0
            new_balance = current_balance - expense.amount
            
            Transaction.objects.create(
                group=group,
                transaction_type='expense',
                expense=expense,
                amount=-expense.amount, # Negative for expenses
                balance_after=new_balance,
                transaction_date=expense.expense_date,
                description=f"Expense: {expense.description}",
                created_by=self.request.user
            )

class LedgerView(generics.ListAPIView):
    """
    View the digital ledger (transactions).
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = self.request.tenant
        if not tenant:
            return Transaction.objects.none()
        group = tenant.groups.first()
        if not group:
            return Transaction.objects.none()
        return Transaction.objects.filter(group=group).order_by('-transaction_date', '-created_at')

class MemberDashboardView(views.APIView):
    """
    Get financial summary for the current member.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tenant = request.tenant
        if not tenant:
            return Response({"error": "No tenant found"}, status=status.HTTP_400_BAD_REQUEST)
        group = tenant.groups.first()
        
        # Calculate totals
        total_contributions = Contribution.objects.filter(
            group=group, 
            member=request.user,
            status='approved'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Get recent transactions
        recent_transactions = Transaction.objects.filter(
            group=group,
            contribution__member=request.user
        ).order_by('-transaction_date')[:5]
        
        return Response({
            "total_contributions": total_contributions,
            "recent_transactions": TransactionSerializer(recent_transactions, many=True).data
        })

class DefaulterListView(generics.ListAPIView):
    """
    List members who have not contributed in the current month.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Allow members to see (transparency) or restrict later
    
    def get_queryset(self):
        tenant = self.request.tenant
        if not tenant:
            return User.objects.none()
        group = tenant.groups.first()
        
        # Get start of current month
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Find members who have contributed this month
        contributors = Contribution.objects.filter(
            group=group,
            contribution_date__gte=start_of_month
        ).values_list('member_id', flat=True)
        
        # Return members NOT in that list
        return User.objects.filter(
            group_memberships__group=group,
            group_memberships__is_active=True
        ).exclude(id__in=contributors)

import csv
from django.http import HttpResponse

class StatementExportView(views.APIView):
    """
    Export financial statement as CSV.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tenant = request.tenant
        if not tenant:
            return Response({"error": "No tenant found"}, status=status.HTTP_400_BAD_REQUEST)
        group = tenant.groups.first()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="statement.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Description', 'Amount', 'Balance'])
        
        transactions = Transaction.objects.filter(group=group).order_by('transaction_date', 'created_at')
        
        for txn in transactions:
            writer.writerow([
                txn.transaction_date,
                txn.transaction_type,
                txn.description,
                txn.amount,
                txn.balance_after
            ])
            
        return response
