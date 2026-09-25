from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.kitchen.models import KitchenOrder
from apps.kitchen.serializers import KitchenOrderSerializer # Make sure this exists
from apps.restaurants.models import RestaurantStaffMember

class KitchenOrderViewSet(viewsets.ModelViewSet):
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'RESTAURANT_STAFF':
            staff_member = RestaurantStaffMember.objects.filter(user=user).first()
            if staff_member:
                return KitchenOrder.objects.filter(order__restaurant=staff_member.restaurant)
            return KitchenOrder.objects.none()
        elif user.role == 'RESTAURANT_OWNER':
            return KitchenOrder.objects.filter(order__restaurant__owner=user)
        elif user.role == 'SUPER_ADMIN':
            return KitchenOrder.objects.all()
        return KitchenOrder.objects.none()