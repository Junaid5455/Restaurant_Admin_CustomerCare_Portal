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
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=30, unique=True, default=generate_order_number, editable=False)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES, default='PICKUP')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PLACED')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
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

    delivery_address = models.TextField(blank=True, null=True)
    delivery_city = models.CharField(max_length=100, blank=True, null=True)
    delivery_state = models.CharField(max_length=100, blank=True, null=True)
    delivery_country = models.CharField(max_length=100, blank=True, null=True)
    delivery_postal_code = models.CharField(max_length=10, blank=True, null=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)

    pickup_time = models.DateTimeField(blank=True, null=True)
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

    def calculate_totals(self):
        """Recalculate subtotal, tax, delivery fee, and total amount"""
        subtotal = sum(item.calculate_subtotal() for item in self.items.all())
        self.subtotal = subtotal
        
        if self.restaurant and self.restaurant.tax_rate:
            self.tax_amount = subtotal * (self.restaurant.tax_rate / 100)
        else:
            self.tax_amount = 0
            
        if self.order_type == 'DELIVERY' and self.restaurant:
            self.delivery_fee = self.restaurant.delivery_fee
        else:
            self.delivery_fee = 0
            
        self.total_amount = subtotal + self.tax_amount + self.delivery_fee - self.discount_amount
        self.save()
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

        # Add this method inside the Order class
    def get_estimated_completion_time(self):
        """Calculate estimated completion time based on order type"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Base preparation time
        eta_minutes = self.estimated_preparation_time_minutes or 30
        
        # Add delivery time if it's a delivery order
        if self.order_type == 'DELIVERY':
            eta_minutes += self.estimated_delivery_time_minutes or 30
            
        return self.placed_at + timedelta(minutes=eta_minutes)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=200)
    item_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity}x {self.item_name}"

    def calculate_subtotal(self):
        self.subtotal = self.item_price * self.quantity
        self.save(update_fields=['subtotal'])
        return self.subtotal


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