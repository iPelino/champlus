"""
Serializers for the financials app.
"""

from rest_framework import serializers
from .models import Contribution, Expense, Transaction
from members.serializers import UserSerializer

class ContributionSerializer(serializers.ModelSerializer):
    """Serializer for Contribution model."""
    member = UserSerializer(read_only=True)
    member_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Contribution
        fields = [
            'id', 'member', 'member_id', 'amount', 'payment_method', 
            'reference_number', 'contribution_date', 'period_start', 
            'period_end', 'status', 'notes', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']

class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model."""
    requested_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'description', 'category', 'amount', 'expense_date', 
            'beneficiary', 'status', 'requested_by', 'notes', 'created_at'
        ]
        read_only_fields = ['status', 'requested_by', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model (Ledger)."""
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'amount', 'balance_after', 
            'transaction_date', 'description', 'created_by', 'created_at'
        ]
