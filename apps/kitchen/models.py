from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel
from apps.orders.models import Order
from apps.restaurants.models import RestaurantStaffMember
from apps.common.choices import KITCHEN_STATUS


class KitchenOrder(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='kitchen_order')
    kitchen_status = models.CharField(max_length=20, choices=KITCHEN_STATUS, default='NEW')
    started_at = models.DateTimeField(blank=True, null=True)
    ready_at = models.DateTimeField(blank=True, null=True)
    collected_at = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(RestaurantStaffMember, on_delete=models.SET_NULL, null=True, blank=True)
    notes_for_kitchen = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.order.order_number

    def mark_started(self):
        self.kitchen_status = 'PREPARING'
        self.started_at = timezone.now()
        self.save()

    def mark_ready(self):
        self.kitchen_status = 'READY'
        self.ready_at = timezone.now()
        self.save()

    def get_preparation_time_elapsed(self):
        if not self.started_at:
            return None
        end_time = self.ready_at or timezone.now()
        return (end_time - self.started_at).total_seconds() / 60