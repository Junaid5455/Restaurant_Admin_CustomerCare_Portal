from django.contrib import admin
from .models import Order, OrderItem, OrderItemCustomization, OrderItemAddOn


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['item_name', 'item_price', 'quantity', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'restaurant', 'customer', 'status', 'payment_status', 'total_amount', 'placed_at']
    list_filter = ['status', 'payment_status', 'order_type', 'placed_at']
    search_fields = ['order_number', 'customer__email', 'restaurant__name']
    readonly_fields = ['placed_at', 'confirmed_at', 'ready_at', 'delivered_at', 'cancelled_at', 'created_at', 'updated_at']
    inlines = [OrderItemInline]