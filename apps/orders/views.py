from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.common.permissions import IsCustomerUser, IsOwnerOfOrder
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer # Make sure this exists
from apps.restaurants.models import RestaurantStaffMember

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsCustomerUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOfOrder]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CUSTOMER':
            return Order.objects.filter(customer=user)
        elif user.role == 'RESTAURANT_OWNER':
            return Order.objects.filter(restaurant__owner=user)
        elif user.role == 'RESTAURANT_STAFF':
            staff_member = RestaurantStaffMember.objects.filter(user=user).first()
            if staff_member:
                return Order.objects.filter(restaurant=staff_member.restaurant)
            return Order.objects.none()
        elif user.role == 'SUPER_ADMIN':
            return Order.objects.all()
        return Order.objects.none()