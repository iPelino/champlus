from rest_framework import serializers
from .models import ApprovalRequest

class ApprovalRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    
    class Meta:
        model = ApprovalRequest
        fields = ['id', 'action_type', 'requester_name', 'status', 'created_at', 'data']
