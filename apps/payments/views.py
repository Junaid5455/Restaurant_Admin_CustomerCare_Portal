from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.common.permissions import IsOwnerOfOrder
from apps.payments.models import Payment, SavedPaymentMethod
from apps.payments.serializers import PaymentSerializer, InitiatePaymentSerializer, ConfirmPaymentSerializer, SavedPaymentMethodSerializer
from apps.payments.services import PaymentService
from apps.orders.models import Order

class PaymentViewSet(viewsets.GenericViewSet):
    """Payment processing endpoints"""
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

    @action(detail=False, methods=['post'], url_path='process')
    def process_payment(self, request):
        """POST /api/v1/payments/process/ - Initiate payment for an order"""
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        order = get_object_or_404(Order, id=data['order_id'], customer=request.user)
        
        if order.payment_status == 'COMPLETED':
            return Response({"error": "Order is already paid"}, status=status.HTTP_400_BAD_REQUEST)

        # If Cash on Delivery, mark order as confirmed immediately
        if data['payment_method'] in ['CASH_ON_DELIVERY', 'CASH_AT_RESTAURANT']:
            payment = Payment.objects.create(
                order=order,
                customer=request.user,
                restaurant=order.restaurant,
                payment_method=data['payment_method'],
                payment_gateway='LOCAL',
                amount=order.total_amount,
                status='PENDING' # Remains pending until restaurant confirms cash received
            )
            order.payment_status = 'PENDING'
            order.status = 'CONFIRMED'
            order.save()
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

        # For Card/Stripe payments
        payment = Payment.objects.create(
            order=order,
            customer=request.user,
            restaurant=order.restaurant,
            payment_method=data['payment_method'],
            payment_gateway='STRIPE',
            amount=order.total_amount,
            status='PENDING'
        )

        try:
            client_secret = PaymentService.create_payment_intent(payment)
            return Response({
                "payment": PaymentSerializer(payment).data,
                "client_secret": client_secret
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_payment(self, request):
        """POST /api/v1/payments/confirm/ - Confirm card payment"""
        serializer = ConfirmPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment = get_object_or_404(Payment, id=serializer.validated_data['payment_id'], customer=request.user)
        
        if payment.status == 'COMPLETED':
            return Response({"message": "Payment already confirmed"}, status=status.HTTP_200_OK)

        try:
            success = PaymentService.confirm_payment(payment)
            if success:
                return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
            return Response({"error": payment.failure_reason or "Payment confirmation failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='refund')
    def refund(self, request, pk=None):
        """POST /api/v1/payments/{id}/refund/ - Process refund"""
        payment = get_object_or_404(Payment, id=pk)
        
        # Only order owner or super admin can refund
        if request.user != payment.order.customer and request.user.role != 'SUPER_ADMIN':
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        if payment.status != 'COMPLETED':
            return Response({"error": "Only completed payments can be refunded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refund_amount = float(request.data.get('amount', payment.amount))
            success = PaymentService.process_refund(payment, refund_amount)
            if success:
                return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
            return Response({"error": "Refund failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """GET /api/v1/payments/{id}/ - View payment details/receipt"""
        payment = get_object_or_404(Payment, id=pk, customer=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)


class SavedPaymentMethodViewSet(viewsets.ModelViewSet):
    """Customer saved payment methods management"""
    serializer_class = SavedPaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedPaymentMethod.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        # If this is set as default, remove default from others
        if serializer.validated_data.get('is_default'):
            SavedPaymentMethod.objects.filter(customer=self.request.user, is_default=True).update(is_default=False)
        serializer.save(customer=self.request.user)