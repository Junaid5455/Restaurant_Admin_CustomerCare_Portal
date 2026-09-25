from rest_framework import serializers
from apps.restaurants.models import Restaurant, RestaurantDeliveryZone
from apps.menu.serializers import MenuCategorySerializer

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