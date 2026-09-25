import random
import string
from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel
from apps.users.models import User
from apps.restaurants.models import Restaurant, RestaurantStaffMember
from apps.orders.models import Order
from apps.common.choices import TICKET_CATEGORIES, TICKET_PRIORITY, TICKET_STATUS, MESSAGE_TYPES


def generate_ticket_id():
    timestamp = timezone.now().strftime("%Y%m%d%H%M")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TKT-{timestamp}-{random_str}"


class SupportTicket(BaseModel):
    ticket_id = models.CharField(max_length=20, unique=True, default=generate_ticket_id, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=TICKET_CATEGORIES)
    priority = models.CharField(max_length=10, choices=TICKET_PRIORITY, default='LOW')
    status = models.CharField(max_length=30, choices=TICKET_STATUS, default='OPEN')
    assigned_to = models.ForeignKey(RestaurantStaffMember, on_delete=models.SET_NULL, null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return self.ticket_id

    def assign_to(self, staff_member):
        self.assigned_to = staff_member
        self.status = 'IN_PROGRESS'
        self.save()

    def resolve(self):
        self.is_resolved = True
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.save()

    def close(self):
        self.status = 'CLOSED'
        self.closed_at = timezone.now()
        self.save()

    def get_days_open(self):
        return (timezone.now() - self.created_at).days


class SupportTicketMessage(BaseModel):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    attachment = models.FileField(upload_to='support_attachments/', blank=True, null=True)

    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"