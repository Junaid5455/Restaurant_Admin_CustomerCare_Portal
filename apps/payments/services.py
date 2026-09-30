import stripe
from django.conf import settings
from django.utils import timezone
from apps.payments.models import Payment
from apps.orders.models import Order

class PaymentService:
    """Service layer for handling payment gateway logic"""
    
    @staticmethod
    def _is_mock_mode():
        """Check if Stripe is configured or if we should use mock mode"""
        return not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY

    @staticmethod
    def create_payment_intent(payment: Payment):
        """Create a Stripe PaymentIntent for the order"""
        if PaymentService._is_mock_mode():
            # Mock mode for local testing without Stripe keys
            payment.transaction_id = "mock_txn_" + str(payment.id).replace('-', '')[:12]
            payment.payment_details_json = {"status": "requires_confirmation", "client_secret": "mock_secret_12345"}
            payment.save()
            return "mock_secret_12345"

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100), # Stripe expects cents
                currency=payment.currency.lower(),
                metadata={'order_id': str(payment.order.id), 'payment_id': str(payment.id)}
            )
            payment.transaction_id = intent.id
            payment.payment_details_json = intent.to_dict()
            payment.save()
            return intent.client_secret
        except stripe.error.StripeError as e:
            payment.status = 'FAILED'
            payment.failure_reason = str(e)
            payment.save()
            raise Exception(f"Stripe Error: {str(e)}")

    @staticmethod
    def confirm_payment(payment: Payment):
        """Verify payment status with Stripe"""
        if PaymentService._is_mock_mode():
            # Mock confirmation
            payment.status = 'COMPLETED'
            payment.paid_at = timezone.now()
            payment.save()
            
            # Update order
            order = payment.order
            order.payment_status = 'COMPLETED'
            order.status = 'CONFIRMED'
            order.save()
            return True

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.retrieve(payment.transaction_id)
            
            if intent.status == 'succeeded':
                payment.status = 'COMPLETED'
                payment.paid_at = timezone.now()
                payment.payment_details_json = intent.to_dict()
                payment.save()
                
                # Update order
                order = payment.order
                order.payment_status = 'COMPLETED'
                order.status = 'CONFIRMED'
                order.save()
                return True
            else:
                payment.status = 'FAILED'
                payment.failure_reason = f"Stripe status: {intent.status}"
                payment.save()
                return False
        except stripe.error.StripeError as e:
            payment.status = 'FAILED'
            payment.failure_reason = str(e)
            payment.save()
            raise Exception(f"Stripe Error: {str(e)}")

    @staticmethod
    def process_refund(payment: Payment, amount=None):
        """Process a refund via Stripe"""
        if PaymentService._is_mock_mode():
            # Mock refund
            payment.status = 'REFUNDED'
            payment.refund_amount = amount or payment.amount
            payment.refunded_at = timezone.now()
            payment.save()
            
            order = payment.order
            order.payment_status = 'REFUNDED'
            order.save()
            return True

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            refund = stripe.Refund.create(
                payment_intent=payment.transaction_id,
                amount=int((amount or payment.amount) * 100)
            )
            
            if refund.status == 'succeeded':
                payment.status = 'REFUNDED'
                payment.refund_amount = amount or payment.amount
                payment.refunded_at = timezone.now()
                payment.save()
                
                order = payment.order
                order.payment_status = 'REFUNDED'
                order.save()
                return True
            return False
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe Refund Error: {str(e)}")