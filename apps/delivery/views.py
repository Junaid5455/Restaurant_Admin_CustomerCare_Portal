from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.delivery.models import Delivery
from apps.delivery.serializers import DeliverySerializer # Make sure this exists

class DeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DELIVERY_STAFF':
            return Delivery.objects.filter(driver__user=user)
        elif user.role == 'RESTAURANT_OWNER':
            return Delivery.objects.filter(restaurant__owner=user)
        elif user.role == 'CUSTOMER':
            return Delivery.objects.filter(customer=user)
        elif user.role == 'SUPER_ADMIN':
            return Delivery.objects.all()
        return Delivery.objects.none()