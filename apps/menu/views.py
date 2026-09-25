from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from apps.menu.models import MenuCategory, MenuItem, MenuItemCustomization
from apps.menu.serializers import MenuCategorySerializer, MenuItemSerializer, MenuItemDetailSerializer, MenuItemCustomizationSerializer

class MenuCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuCategory.objects.filter(is_active=True)
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant_id')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset.order_by('order', 'name')

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def items(self, request, pk=None):
        """Get all items in this category: /api/v1/menu/categories/{id}/items/"""
        category = self.get_object()
        items = MenuItem.objects.filter(category=category, is_available=True).order_by('name')
        
        paginator = PageNumberPagination()
        paginated_items = paginator.paginate_queryset(items, request)
        serializer = MenuItemSerializer(paginated_items, many=True)
        return paginator.get_paginated_response(serializer.data)


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(is_available=True, restaurant__is_active=True)
    serializer_class = MenuItemDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_vegetarian', 'is_vegan', 'is_spicy', 'is_featured', 'restaurant', 'category']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'rating', 'preparation_time_minutes']
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MenuItemSerializer
        return MenuItemDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related('restaurant', 'category').prefetch_related('customizations__options', 'addons')
        
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset.order_by('category__order', 'name')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def featured(self, request):
        """Get featured menu items: /api/v1/menu/items/featured/"""
        items = self.get_queryset().filter(is_featured=True)[:10]
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def customizations(self, request, pk=None):
        """Get item customization options: /api/v1/menu/items/{id}/customizations/"""
        item = self.get_object()
        customizations = MenuItemCustomization.objects.filter(menu_item=item)
        serializer = MenuItemCustomizationSerializer(customizations, many=True)
        return Response(serializer.data)