"""
Management command to send contribution reminders.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from tenants.models import Tenant
from financials.models import Contribution
from notifications.utils import send_notification
from datetime import timedelta

class Command(BaseCommand):
    help = 'Sends reminders to members who have not contributed in the current period.'

    def handle(self, *args, **options):
        self.stdout.write("Starting reminder checks...")
        
        # Get start of current month
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        active_tenants = Tenant.objects.filter(is_active=True)
        
        count = 0
        for tenant in active_tenants:
            group = tenant.groups.first()
            if not group:
                continue
                
            # Find members who have contributed this month
            contributors = Contribution.objects.filter(
                group=group,
                contribution_date__gte=start_of_month
            ).values_list('member_id', flat=True)
            
            # Find members who have NOT contributed
            defaulters = User.objects.filter(
                group_memberships__group=group,
                group_memberships__is_active=True
            ).exclude(id__in=contributors)
            
            for member in defaulters:
                subject = f"Reminder: Contribution Due for {group.name}"
                message = f"Hello {member.first_name},\n\nThis is a friendly reminder to make your contribution of {group.currency} {group.contribution_amount} for this month.\n\nThank you!"
                
                if send_notification(member, subject, message, notification_type='email'):
                    count += 1
                    
        self.stdout.write(self.style.SUCCESS(f"Sent {count} reminders."))
