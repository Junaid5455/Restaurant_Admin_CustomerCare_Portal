from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from apps.common.permissions import CanManageRestaurant, IsRestaurantOwner
from apps.restaurants.models import Restaurant, RestaurantDeliveryZone
from apps.restaurants.serializers import RestaurantDetailSerializer, RestaurantListSerializer, RestaurantDeliveryZoneSerializer
from apps.menu.models import MenuCategory
from apps.menu.serializers import MenuCategoryDetailSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['allows_delivery', 'allows_pickup', 'is_active'] # Removed 'is_featured'
    search_fields = ['name', 'description', 'city', 'state']
    ordering_fields = ['name', 'rating', 'delivery_fee', 'created_at']
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsRestaurantOwner]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [CanManageRestaurant]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantListSerializer
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantDetailSerializer

    def get_queryset(self):
        user = self.request.user
        
        # Owners managing their restaurant see all their own restaurants
        if user.is_authenticated and user.role == 'RESTAURANT_OWNER' and self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return Restaurant.objects.filter(owner=user).select_related('owner').prefetch_related('delivery_zones')
            
        # Customers and Anonymous users only see active restaurants
        queryset = Restaurant.objects.filter(is_active=True).select_related('owner').prefetch_related('delivery_zones')
        
        # Filter by delivery availability
        delivery_only = self.request.query_params.get('delivery_only')
        if delivery_only and delivery_only.lower() == 'true':
            queryset = queryset.filter(allows_delivery=True)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def menu(self, request, pk=None):
        """Get restaurant menu (categories and their active items)"""
        restaurant = self.get_object()
        categories = MenuCategory.objects.filter(
            restaurant=restaurant,
            is_active=True
        ).prefetch_related('items')
        
        serializer = MenuCategoryDetailSerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def delivery_zones(self, request, pk=None):
        """Get restaurant delivery zones"""
        restaurant = self.get_object()
        zones = RestaurantDeliveryZone.objects.filter(restaurant=restaurant, is_active=True)
        
        serializer = RestaurantDeliveryZoneSerializer(zones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def search(self, request):
        """Advanced restaurant search endpoint: /api/v1/restaurants/search/?q=query"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'error': 'Search query too short (min 2 chars)'}, status=status.HTTP_400_BAD_REQUEST)
        
        restaurants = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query)
        )[:20]
        
        serializer = RestaurantListSerializer(restaurants, many=True)
        return Response({
            'restaurants': serializer.data,
            'count': len(restaurants)
        })