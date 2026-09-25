from django.contrib import admin
from .models import KitchenOrder


@admin.register(KitchenOrder)
class KitchenOrderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'kitchen_status', 'assigned_to', 'started_at', 'ready_at']
    list_filter = ['kitchen_status']
    search_fields = ['order__order_number']