from rest_framework import serializers
from apps.payments.models import Payment, SavedPaymentMethod
from apps.orders.models import Order

class SavedPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPaymentMethod
        fields = ['id', 'customer', 'payment_method_type', 'is_default', 'card_last_four', 'card_brand', 'card_expiry_month', 'card_expiry_year', 'token']
        read_only_fields = ['customer', 'card_last_four', 'card_brand', 'token']
        extra_kwargs = {
            'card_expiry_month': {'required': False},
            'card_expiry_year': {'required': False}
        }

class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'customer', 'restaurant', 'payment_method', 
            'payment_gateway', 'transaction_id', 'amount', 'currency', 'status', 
            'failure_reason', 'refund_amount', 'paid_at', 'created_at'
        ]
        read_only_fields = [
            'customer', 'restaurant', 'transaction_id', 'amount', 'currency', 
            'status', 'failure_reason', 'refund_amount', 'paid_at'
        ]

class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField(required=True)
    payment_method = serializers.ChoiceField(choices=['CREDIT_CARD', 'DEBIT_CARD', 'STRIPE', 'CASH_ON_DELIVERY', 'CASH_AT_RESTAURANT'])

class ConfirmPaymentSerializer(serializers.Serializer):
    payment_id = serializers.UUIDField(required=True)