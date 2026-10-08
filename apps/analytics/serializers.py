from rest_framework import serializers
from apps.orders.models import Order
from apps.menu.models import MenuItem

class PopularItemSerializer(serializers.Serializer):
    """Serializer for popular items aggregation"""
    id = serializers.UUIDField()
    name = serializers.CharField()
    total_quantity_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

class RecentOrderSerializer(serializers.ModelSerializer):
    """Lightweight serializer for recent orders"""
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer_email', 'status', 'total_amount', 'items_count', 'placed_at']

class SalesReportSerializer(serializers.Serializer):
    """Serializer for sales reports"""
    date = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)

class CustomerAnalyticsSerializer(serializers.Serializer):
    """Serializer for customer analytics"""
    customer_id = serializers.UUIDField()
    customer_email = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)

class OperationalMetricsSerializer(serializers.Serializer):
    """Serializer for operational metrics"""
    peak_hour = serializers.IntegerField()
    order_count = serializers.IntegerField()