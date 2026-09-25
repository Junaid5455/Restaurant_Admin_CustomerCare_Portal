from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.orders.models import Order
from apps.common.choices import PAYMENT_METHODS, PAYMENT_GATEWAYS, PAYMENT_STATUS


class Payment(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_gateway = models.CharField(max_length=20, choices=PAYMENT_GATEWAYS, default='LOCAL')
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    failure_reason = models.TextField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    payment_details_json = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['restaurant']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment for {self.order.order_number}"

    def mark_completed(self):
        self.status = 'COMPLETED'
        self.paid_at = timezone.now()
        self.save()

    def mark_failed(self, reason):
        self.status = 'FAILED'
        self.failure_reason = reason
        self.save()

    def process_refund(self, amount, reason):
        self.status = 'REFUNDED'
        self.refund_amount = amount
        self.refund_reason = reason
        self.refunded_at = timezone.now()
        self.save()

    def is_paid(self):
        return self.status == 'COMPLETED'


class SavedPaymentMethod(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_payment_methods')
    payment_method_type = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    is_default = models.BooleanField(default=False)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=50, blank=True, null=True)
    card_expiry_month = models.IntegerField(blank=True, null=True)
    card_expiry_year = models.IntegerField(blank=True, null=True)
    token = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.card_brand} ending in {self.card_last_four}"