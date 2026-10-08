import secrets
import string
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from apps.common.permissions import CanManageRestaurant, IsRestaurantOwner
from apps.restaurants.models import RestaurantStaffMember ,Restaurant, RestaurantDeliveryZone,  RestaurantHoliday
from apps.restaurants.serializers import RestaurantDetailSerializer, RestaurantListSerializer, RestaurantDeliveryZoneSerializer, RestaurantSettingsSerializer, RestaurantHolidaySerializer, StaffMemberSerializer
from apps.menu.models import MenuCategory
from apps.menu.serializers import MenuCategoryDetailSerializer
from rest_framework.exceptions import ValidationError
from apps.users.models import User




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




class RestaurantSettingsView(APIView):
    """Get or Update restaurant settings"""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get(self, request):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        serializer = RestaurantSettingsSerializer(restaurant)
        return Response(serializer.data)

    def patch(self, request):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        serializer = RestaurantSettingsSerializer(restaurant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RestaurantHolidayViewSet(viewsets.ModelViewSet):
    """Manage restaurant holidays/closures"""
    serializer_class = RestaurantHolidaySerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        return RestaurantHoliday.objects.filter(restaurant__owner=self.request.user)

    def perform_create(self, serializer):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        serializer.save(restaurant=restaurant)

class RestaurantDeliveryZoneViewSet(viewsets.ModelViewSet):
    """Manage restaurant delivery zones"""
    serializer_class = RestaurantDeliveryZoneSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        return RestaurantDeliveryZone.objects.filter(restaurant__owner=self.request.user)

    def perform_create(self, serializer):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        serializer.save(restaurant=restaurant)



class StaffMemberViewSet(viewsets.ModelViewSet):
    """Manage restaurant staff"""
    serializer_class = StaffMemberSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        return RestaurantStaffMember.objects.filter(restaurant__owner=self.request.user)

    def perform_create(self, serializer):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        staff_email = self.request.data.get('staff_email')
        
        if not staff_email:
            raise ValidationError({"staff_email": "This field is required."})
            
        # Look for existing user, or create a new one if they don't exist
        user, created = User.objects.get_or_create(
            email=staff_email,
            defaults={
                'role': 'RESTAURANT_STAFF',
                'is_active': True
            }
        )
        
        # If the user was already a customer, upgrade their role to staff
        if not created and user.role not in ['RESTAURANT_STAFF', 'DELIVERY_STAFF', 'RESTAURANT_OWNER', 'SUPER_ADMIN']:
            user.role = 'RESTAURANT_STAFF'
            user.save()
            
        # Prevent duplicate staff entries
        if RestaurantStaffMember.objects.filter(restaurant=restaurant, user=user).exists():
            raise ValidationError("This user is already a staff member at your restaurant.")
        
        # Pop 'staff_email' from validated data so it doesn't get passed to the DB
        validated_data = serializer.validated_data
        validated_data.pop('staff_email', None)
            
        serializer.save(restaurant=restaurant, user=user)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """POST /api/v1/restaurants/staff/{id}/toggle-active/"""
        staff_member = self.get_object()
        staff_member.is_active = not staff_member.is_active
        staff_member.save()
        
        return Response({"is_active": staff_member.is_active}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-permissions')
    def update_permissions(self, request, pk=None):
        """POST /api/v1/restaurants/staff/{id}/update-permissions/"""
        staff_member = self.get_object()
        
        permissions = ['can_manage_menu', 'can_manage_orders', 'can_manage_staff', 'can_manage_payments', 'can_view_analytics']
        for perm in permissions:
            if perm in request.data:
                setattr(staff_member, perm, request.data[perm])
        
        staff_member.save()
        serializer = self.get_serializer(staff_member)
        return Response(serializer.data, status=status.HTTP_200_OK)