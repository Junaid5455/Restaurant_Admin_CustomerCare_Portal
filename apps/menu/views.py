from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.common.permissions import CanManageRestaurant
from apps.menu.models import MenuCategory, MenuItem
from apps.menu.serializers import MenuCategorySerializer, MenuItemSerializer # Make sure these exist

class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [CanManageRestaurant]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = MenuCategory.objects.all()
        if self.request.user.is_authenticated and self.request.user.role == 'RESTAURANT_OWNER':
            return queryset.filter(restaurant__owner=self.request.user)
        return queryset.filter(restaurant__is_active=True)

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [CanManageRestaurant]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        if self.request.user.is_authenticated and self.request.user.role == 'RESTAURANT_OWNER':
            return queryset.filter(restaurant__owner=self.request.user)
        return queryset.filter(is_available=True)