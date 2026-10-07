from rest_framework import serializers
from apps.orders.models import Order, OrderItem, OrderItemCustomization, OrderItemAddOn

class KitchenItemCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemCustomization
        fields = ['customization_name', 'option_name']

class KitchenItemAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemAddOn
        fields = ['addon_name']

class KitchenOrderItemSerializer(serializers.ModelSerializer):
    customizations = KitchenItemCustomizationSerializer(many=True, read_only=True)
    add_ons = KitchenItemAddOnSerializer(many=True, read_only=True, source='addons')
    
    class Meta:
        model = OrderItem
        fields = ['id', 'item_name', 'quantity', 'special_instructions', 'customizations', 'add_ons']

class KitchenOrderSerializer(serializers.ModelSerializer):
    """Serializer for the Kitchen Display System"""
    items = KitchenOrderItemSerializer(many=True, read_only=True)
    order_type = serializers.CharField()
    table_number = serializers.CharField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_type', 'table_number', 'status', 
            'placed_at', 'confirmed_at', 'items'
        ]