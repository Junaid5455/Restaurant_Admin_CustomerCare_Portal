from django.contrib import admin
from .models import Payment, SavedPaymentMethod


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'customer', 'restaurant', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_gateway']
    search_fields = ['order__order_number', 'customer__email', 'transaction_id']


@admin.register(SavedPaymentMethod)
class SavedPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['customer', 'payment_method_type', 'card_brand', 'card_last_four', 'is_default']
    list_filter = ['is_default', 'card_brand']