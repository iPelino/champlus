from rest_framework import serializers
from .models import Loan, Repayment
from django.contrib.auth.models import User

class LoanSerializer(serializers.ModelSerializer):
    borrower_name = serializers.ReadOnlyField(source='borrower.get_full_name')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.get_full_name')
    
    class Meta:
        model = Loan
        fields = [
            'id', 'group', 'borrower', 'borrower_name', 'amount', 'interest_rate',
            'duration_months', 'status', 'requested_at', 'approved_at',
            'disbursed_at', 'due_date', 'approved_by', 'approved_by_name',
            'total_amount_payable', 'amount_paid'
        ]
        read_only_fields = [
            'id', 'group', 'borrower', 'status', 'requested_at', 'approved_at',
            'disbursed_at', 'due_date', 'approved_by', 'total_amount_payable', 'amount_paid'
        ]

class RepaymentSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.ReadOnlyField(source='recorded_by.get_full_name')
    
    class Meta:
        model = Repayment
        fields = [
            'id', 'loan', 'amount', 'paid_at', 'recorded_by', 'recorded_by_name', 'notes'
        ]
        read_only_fields = ['id', 'paid_at', 'recorded_by']
