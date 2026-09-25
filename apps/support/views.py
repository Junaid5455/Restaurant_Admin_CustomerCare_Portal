from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.support.models import SupportTicket
from apps.support.serializers import SupportTicketSerializer # Make sure this exists

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CUSTOMER':
            return SupportTicket.objects.filter(customer=user)
        elif user.role == 'RESTAURANT_OWNER':
            return SupportTicket.objects.filter(restaurant__owner=user)
        elif user.role == 'SUPER_ADMIN':
            return SupportTicket.objects.all()
        return SupportTicket.objects.none()