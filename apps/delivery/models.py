from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel
from apps.orders.models import Order
from apps.users.models import User
from apps.restaurants.models import Restaurant, RestaurantStaffMember
from apps.common.choices import DELIVERY_STATUS


class Delivery(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    driver = models.ForeignKey(RestaurantStaffMember, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='PENDING')
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    estimated_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_delivery_time_minutes = models.IntegerField()
    actual_delivery_time_minutes = models.IntegerField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=200, blank=True, null=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    delivery_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    delivery_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['driver']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Delivery for {self.order.order_number}"

    def assign_driver(self, driver):
        self.driver = driver
        self.status = 'ASSIGNED'
        self.assigned_at = timezone.now()
        self.save()

    def update_location(self, latitude, longitude):
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_location_update = timezone.now()
        self.save()

    def mark_picked_up(self):
        self.status = 'PICKED_UP'
        self.picked_up_at = timezone.now()
        self.save()

    def mark_delivered(self):
        self.status = 'DELIVERED'
        self.delivered_at = timezone.now()
        self.save()