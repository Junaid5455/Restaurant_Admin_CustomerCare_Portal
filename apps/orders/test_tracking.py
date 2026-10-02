from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem
import decimal

class OrderTrackingTests(APITestCase):
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
        
        # Create a placed order
        self.order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            order_type='PICKUP',
            status='PLACED',
            payment_status='COMPLETED',
            subtotal=decimal.Decimal('10.00'),
            tax_amount=decimal.Decimal('0.50'),
            total_amount=decimal.Decimal('10.50'),
            estimated_preparation_time_minutes=20
        )
        OrderItem.objects.create(
            order=self.order, menu_item=self.item, item_name="Margherita", 
            item_price=decimal.Decimal('10.00'), quantity=1, subtotal=decimal.Decimal('10.00')
        )
        
        self.client.force_authenticate(user=self.customer)

    def test_track_order(self):
        url = f'/api/v1/orders/{self.order.id}/track/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_number'], self.order.order_number)
        self.assertEqual(response.data['status'], 'PLACED')
        self.assertEqual(response.data['restaurant_name'], "Test Pizza")
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['name'], "Margherita")
        # Check that ETA is returned
        self.assertIsNotNone(response.data['estimated_completion_time'])

    def test_order_history_list(self):
        # Ensure cart is excluded from history
        Order.objects.create(customer=self.customer, restaurant=self.restaurant, status='CART')
        
        url = '/api/v1/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return 1 (the PLACED order, not the CART)
        # Our CustomPagination wraps the list inside a 'data' key
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['status'], 'PLACED')