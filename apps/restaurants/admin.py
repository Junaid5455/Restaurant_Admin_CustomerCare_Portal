from django.contrib import admin
from .models import Restaurant, RestaurantHoliday, RestaurantDeliveryZone, RestaurantStaffMember


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'city']
    search_fields = ['name', 'owner__email']
    readonly_fields = ['created_at', 'updated_at', 'slug', 'rating', 'total_reviews']
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'owner', 'description', 'logo', 'banner')}),
        ('Contact', {'fields': ('email', 'phone', 'website')}),
        ('Location', {'fields': ('address', 'city', 'state', 'country', 'postal_code', 'latitude', 'longitude')}),
        ('Operations', {'fields': ('opening_time', 'closing_time', 'is_open', 'is_active', 'allows_pickup', 'allows_delivery', 'allows_dine_in')}),
        ('Financials', {'fields': ('min_order_amount', 'delivery_fee', 'delivery_time_minutes', 'tax_rate')}),
        ('Metrics', {'fields': ('rating', 'total_reviews')}),
    )


@admin.register(RestaurantStaffMember)
class RestaurantStaffMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__email', 'restaurant__name']