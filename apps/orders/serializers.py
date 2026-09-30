from rest_framework import serializers
from apps.orders.models import Order, OrderItem, OrderItemCustomization, OrderItemAddOn
from apps.menu.models import MenuItem, MenuItemCustomizationOption, MenuItemAddOn
from decimal import Decimal

class OrderItemCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemCustomization
        fields = ['id', 'customization_name', 'option_name', 'price_modifier']

class OrderItemAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemAddOn
        fields = ['id', 'addon_name', 'addon_price']

class OrderItemSerializer(serializers.ModelSerializer):
    customizations = OrderItemCustomizationSerializer(many=True, read_only=True)
    add_ons = OrderItemAddOnSerializer(many=True, read_only=True, source='addons')
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'item_name', 'item_price', 'quantity', 'subtotal', 'special_instructions', 'customizations', 'add_ons']
        read_only_fields = ['item_name', 'item_price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'restaurant', 'restaurant_name', 'customer', 
            'order_type', 'status', 'payment_status', 'subtotal', 'tax_amount', 
            'delivery_fee', 'total_amount', 'items', 'created_at'
        ]
        read_only_fields = ['order_number', 'subtotal', 'tax_amount', 'delivery_fee', 'total_amount']

class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart with customizations and addons"""
    menu_item_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    special_instructions = serializers.CharField(required=False, allow_blank=True)
    customization_option_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
    addon_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )

    def validate(self, attrs):
        # Validate menu item exists and is available
        try:
            menu_item = MenuItem.objects.get(id=attrs['menu_item_id'], is_available=True)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Menu item not available.")
        
        attrs['menu_item'] = menu_item
        return attrs

class CartSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'restaurant', 'restaurant_name', 'order_type', 
            'status', 'subtotal', 'tax_amount', 'delivery_fee', 'total_amount', 
            'items', 'created_at'
        ]
        read_only_fields = ['order_number', 'subtotal', 'tax_amount', 'delivery_fee', 'total_amount']