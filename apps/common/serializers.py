"""
Base serializer classes for the Restaurant Portal API.
"""
from rest_framework import serializers
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.orders.models import Order


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for all model serializers.

    Includes read-only timestamp fields and standard error
    message formatting.
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        read_only_fields = ("id", "created_at", "updated_at")


class TimestampSerializerMixin(serializers.Serializer):
    """
    Mixin to add timestamp fields to any serializer.

    Usage:
        class MySerializer(TimestampSerializerMixin, serializers.Serializer):
            ...
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        fields = ("id", "created_at", "updated_at")


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    ModelSerializer that takes an additional `fields` argument
    to dynamically control which fields are included.

    Usage:
        class MySerializer(DynamicFieldsModelSerializer):
            ...
        # Then in the view:
        serializer = MySerializer(obj, fields=('id', 'name'))
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)




class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'date_joined']

class AdminRestaurantSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'owner_email', 'is_active', 'city', 'created_at']

class AdminOrderSerializer(serializers.ModelSerializer):
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer_email', 'restaurant_name', 'status', 'total_amount', 'placed_at']