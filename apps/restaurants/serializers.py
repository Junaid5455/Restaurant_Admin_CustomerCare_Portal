from rest_framework import serializers
from apps.restaurants.models import Restaurant, RestaurantHoliday, RestaurantDeliveryZone, RestaurantStaffMember

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
        # Add 'owner' to read_only_fields so it's not required in the POST request
        read_only_fields = ['slug', 'rating', 'total_reviews', 'created_at', 'updated_at', 'owner']

class RestaurantHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantHoliday
        fields = '__all__'

class RestaurantDeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantDeliveryZone
        fields = '__all__'

class RestaurantStaffMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantStaffMember
        fields = '__all__'