from rest_framework import serializers
from apps.menu.serializers import MenuCategorySerializer
from apps.restaurants.models import Restaurant, RestaurantHoliday, RestaurantDeliveryZone, RestaurantStaffMember



class RestaurantDeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantDeliveryZone
        fields = ['id', 'zone_name', 'delivery_fee', 'delivery_time_minutes', 'postal_codes', 'is_active']

class RestaurantListSerializer(serializers.ModelSerializer):
    is_open_now = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(source='total_reviews', read_only=True)
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'logo', 'rating', 'review_count', 
            'is_open_now', 'delivery_time_minutes', 'min_order_amount'
            # Removed 'is_featured'
        ]
    
    def get_is_open_now(self, obj):
        from django.utils import timezone
        current_time = timezone.now().time()
        return obj.opening_time <= current_time <= obj.closing_time

class RestaurantDetailSerializer(serializers.ModelSerializer):
    is_open_now = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(source='total_reviews', read_only=True)
    delivery_zones = RestaurantDeliveryZoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'logo', 'banner', 'description', 'email', 'phone',
            'address', 'city', 'state', 'country', 'postal_code', 'opening_time', 'closing_time',
            'rating', 'review_count', 'is_open_now', 'delivery_time_minutes', 'delivery_fee', 
            'min_order_amount', 'allows_pickup', 'allows_delivery', 'allows_dine_in', 
            'is_active', 'delivery_zones'
            # Removed 'is_featured'
        ]
    
    def get_is_open_now(self, obj):
        from django.utils import timezone
        current_time = timezone.now().time()
        return obj.opening_time <= current_time <= obj.closing_time




class RestaurantSettingsSerializer(serializers.ModelSerializer):
    """Serializer for restaurant owner to update settings"""
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'description', 'logo', 'banner', 'email', 'phone',
            'address', 'city', 'state', 'country', 'postal_code', 
            'opening_time', 'closing_time', 'is_open',
            'allows_pickup', 'allows_delivery', 'allows_dine_in',
            'min_order_amount', 'delivery_fee', 'delivery_time_minutes', 'tax_rate',
            
        ]
        read_only_fields = ['id']

class RestaurantHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantHoliday
        fields = ['id', 'holiday_date', 'reason', 'created_at']
        read_only_fields = ['created_at']

class RestaurantDeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantDeliveryZone
        fields = ['id', 'zone_name', 'delivery_fee', 'delivery_time_minutes', 'postal_codes', 'is_active']



class StaffMemberSerializer(serializers.ModelSerializer):
    """Serializer for managing restaurant staff"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    staff_email = serializers.EmailField(write_only=True, required=False)
    
    class Meta:
        model = RestaurantStaffMember
        fields = [
            'id', 'user_email', 'staff_email', 'role', 'is_active', 
            'can_manage_menu', 'can_manage_orders', 'can_manage_staff', 
            'can_manage_payments', 'can_view_analytics', 'created_at'
        ]
        read_only_fields = ['is_active', 'created_at']