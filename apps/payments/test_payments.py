from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings # <-- ADDED IMPORT
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order
import decimal

@override_settings(STRIPE_SECRET_KEY="") # <-- ADDED DECORATOR TO FORCE MOCK MODE
class PaymentTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        self.category = MenuCategory.objects.create(restaurant=self.restaurant, name="Pizzas")
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Margherita", 
            description="Cheese", price=decimal.Decimal('10.00'), is_available=True
        )
        
        # Create a placed order to pay for
        self.order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            order_type='PICKUP',
            status='PLACED',
            payment_status='PENDING',
            subtotal=decimal.Decimal('10.00'),
            tax_amount=decimal.Decimal('0.50'),
            total_amount=decimal.Decimal('10.50')
        )
        
        self.client.force_authenticate(user=self.customer)

    def test_initiate_card_payment_mock(self):
        # 1. Add item to cart
        self.client.post('/api/v1/orders/cart/items/', {"menu_item_id": str(self.item.id), "quantity": 1}, format='json')
        # 2. Checkout
        checkout_res = self.client.post('/api/v1/orders/cart/checkout/', {"order_type": "PICKUP", "pickup_time": "2026-10-01T18:00:00Z"}, format='json')
        order_id = checkout_res.data['order_id']
        
        # 3. Process payment
        response = self.client.post('/api/v1/payments/process/', {
            "order_id": order_id,
            "payment_method": "CREDIT_CARD"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment']['status'], 'PENDING')
        self.assertEqual(response.data['client_secret'], 'mock_secret_12345')

    def test_confirm_card_payment_mock(self):
        # Setup payment first
        payment_res = self.client.post('/api/v1/payments/process/', {
            "order_id": str(self.order.id),
            "payment_method": "CREDIT_CARD"
        }, format='json')
        payment_id = payment_res.data['payment']['id']
        
        # Confirm payment
        response = self.client.post('/api/v1/payments/confirm/', {
            "payment_id": payment_id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'COMPLETED')
        
        # Verify order status updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'COMPLETED')
        self.assertEqual(self.order.status, 'CONFIRMED')

    def test_cash_on_delivery_flow(self):
        response = self.client.post('/api/v1/payments/process/', {
            "order_id": str(self.order.id),
            "payment_method": "CASH_ON_DELIVERY"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING') # Remains pending until cash given
        
        # Verify order is confirmed immediately
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CONFIRMED')

    def test_refund_flow(self):
        # 1. Pay first
        payment_res = self.client.post('/api/v1/payments/process/', {
            "order_id": str(self.order.id),
            "payment_method": "CREDIT_CARD"
        }, format='json')
        payment_id = payment_res.data['payment']['id']
        self.client.post('/api/v1/payments/confirm/', {"payment_id": payment_id}, format='json')
        
        # 2. Refund
        response = self.client.post(f'/api/v1/payments/{payment_id}/refund/', {"amount": "10.50"}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'REFUNDED')
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'REFUNDED')