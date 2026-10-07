from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.common.permissions import IsRestaurantOwner
from apps.restaurants.models import Restaurant
from apps.orders.models import Order
from apps.menu.models import MenuItem
from apps.analytics.serializers import PopularItemSerializer, RecentOrderSerializer

class DashboardViewSet(viewsets.ViewSet):
    """Analytics endpoints for the Restaurant Owner Dashboard"""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get_restaurant(self, request):
        """Helper method to get the owner's restaurant"""
        try:
            return Restaurant.objects.get(owner=request.user)
        except Restaurant.DoesNotExist:
            return None

    def list(self, request):
        """GET /api/v1/analytics/dashboard/ - Main overview stats"""
        restaurant = self.get_restaurant(request)
        if not restaurant:
            return Response({"error": "No restaurant found for this user"}, status=status.HTTP_404_NOT_FOUND)

        # Calculate start and end of today
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Fetch orders
        all_orders = Order.objects.filter(restaurant=restaurant).exclude(status='CART')
        today_orders = all_orders.filter(placed_at__gte=today_start, placed_at__lt=today_end)

        # Aggregations
        total_sales = all_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        today_sales = today_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        total_orders = all_orders.count()
        today_orders_count = today_orders.count()

        # Order Status counts for today
        pending_orders = today_orders.filter(status__in=['PLACED', 'CONFIRMED', 'PREPARING']).count()
        completed_orders = today_orders.filter(status='DELIVERED').count()
        cancelled_orders = today_orders.filter(status='CANCELLED').count()

        # Customer count (unique customers who ordered)
        total_customers = all_orders.values('customer').distinct().count()

        data = {
            "restaurant_name": restaurant.name,
            "today_sales": str(today_sales),
            "today_orders_count": today_orders_count,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_sales": str(total_sales),
            "total_orders": total_orders,
            "total_customers": total_customers,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def popular_items(self, request):
        """GET /api/v1/analytics/dashboard/popular_items/ - Top 5 selling items"""
        restaurant = self.get_restaurant(request)
        if not restaurant:
            return Response({"error": "No restaurant found"}, status=status.HTTP_404_NOT_FOUND)

        # Aggregate order items to find most sold
        popular = MenuItem.objects.filter(restaurant=restaurant).annotate(
            total_quantity_sold=Sum('orderitem__quantity'),
            total_revenue=Sum('orderitem__subtotal')
        ).filter(total_quantity_sold__gt=0).order_by('-total_quantity_sold')[:5]

        serializer = PopularItemSerializer(popular, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recent_orders(self, request):
        """GET /api/v1/analytics/dashboard/recent_orders/ - Last 5 orders"""
        restaurant = self.get_restaurant(request)
        if not restaurant:
            return Response({"error": "No restaurant found"}, status=status.HTTP_404_NOT_FOUND)

        # Update the order_by to include '-created_at' as a tie-breaker
        recent = Order.objects.filter(restaurant=restaurant).exclude(status='CART').order_by('-placed_at', '-created_at')[:5]
        serializer = RecentOrderSerializer(recent, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)