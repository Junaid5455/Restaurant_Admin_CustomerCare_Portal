import random
import string
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.common.models import BaseModel
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem
from apps.common.choices import ORDER_TYPES, ORDER_STATUS, PAYMENT_STATUS


def generate_order_number():
    timestamp = timezone.now().strftime("%Y%m%d%H%M")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{timestamp}-{random_str}"


class Order(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, default=generate_order_number, editable=False)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PLACED')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    estimated_preparation_time_minutes = models.IntegerField(default=30)
    estimated_delivery_time_minutes = models.IntegerField(blank=True, null=True)
    actual_delivery_time_minutes = models.IntegerField(blank=True, null=True)
    
    customer_notes = models.TextField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    placed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    ready_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.CharField(max_length=200, blank=True, null=True)

    # Delivery specific
    delivery_address = models.TextField(blank=True, null=True)
    delivery_city = models.CharField(max_length=100, blank=True, null=True)
    delivery_state = models.CharField(max_length=100, blank=True, null=True)
    delivery_country = models.CharField(max_length=100, blank=True, null=True)
    delivery_postal_code = models.CharField(max_length=10, blank=True, null=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)

    # Pickup specific
    pickup_time = models.DateTimeField(blank=True, null=True)

    # Dine-in specific
    table_number = models.CharField(max_length=10, blank=True, null=True)
    number_of_guests = models.IntegerField(blank=True, null=True)

    is_scheduled = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-placed_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['restaurant']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.order_number

    def clean(self):
        if self.order_type == 'DELIVERY' and not self.delivery_address:
            raise ValidationError("Delivery orders must have a delivery address.")
        if self.order_type == 'PICKUP' and not self.pickup_time:
            raise ValidationError("Pickup orders must have a pickup time.")
        if self.order_type == 'DINE_IN' and not self.table_number:
            raise ValidationError("Dine-in orders must have a table number.")
        
        expected_total = self.subtotal + self.tax_amount + self.delivery_fee - self.discount_amount
        if self.total_amount != expected_total:
            raise ValidationError(f"Total amount mismatch. Expected {expected_total}, got {self.total_amount}")

    def calculate_total(self):
        self.total_amount = self.subtotal + self.tax_amount + self.delivery_fee - self.discount_amount
        self.save(update_fields=['total_amount'])
        return self.total_amount

    def update_status(self, new_status):
        self.status = new_status
        if new_status == 'CONFIRMED':
            self.confirmed_at = timezone.now()
        elif new_status == 'READY':
            self.ready_at = timezone.now()
        elif new_status == 'DELIVERED':
            self.delivered_at = timezone.now()
        elif new_status == 'CANCELLED':
            self.cancelled_at = timezone.now()
        self.save()

    def can_be_cancelled(self):
        return self.status in ['PLACED', 'CONFIRMED']


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=200)
    item_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity}x {self.item_name}"

    def calculate_subtotal(self):
        return self.item_price * self.quantity


class OrderItemCustomization(BaseModel):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='customizations')
    customization_name = models.CharField(max_length=100)
    option_name = models.CharField(max_length=100)
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.customization_name}: {self.option_name}"


class OrderItemAddOn(BaseModel):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='addons')
    addon_name = models.CharField(max_length=100)
    addon_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.addon_name