from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.common.permissions import CanManageRestaurant, IsRestaurantOwner
from apps.restaurants.models import Restaurant
from apps.restaurants.serializers import RestaurantSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsRestaurantOwner]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [CanManageRestaurant]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        
        # For list actions, strictly filter what users can see
        if self.action == 'list':
            if user.is_authenticated:
                if user.role == 'RESTAURANT_OWNER':
                    return Restaurant.objects.filter(owner=user)
                elif user.role == 'SUPER_ADMIN':
                    return Restaurant.objects.all()
            return Restaurant.objects.filter(is_active=True)
        
        # For retrieve, update, delete: return ALL restaurants so the 
        # CanManageRestaurant permission class can evaluate and return a 403 
        # instead of a 404 if they try to hack someone else's restaurant.
        return Restaurant.objects.all()

    def perform_create(self, serializer):
        # Automatically set the owner to the logged-in user
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[CanManageRestaurant])
    def analytics(self, request, pk=None):
        restaurant = self.get_object()
        return Response({'sales': 1000, 'orders': 50})