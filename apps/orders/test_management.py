from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem
import decimal

class OrderManagementTests(APITestCase):
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
            customer=self.customer, restaurant=self.restaurant, order_type='PICKUP', 
            status='PLACED', payment_status='COMPLETED', total_amount=decimal.Decimal('10.50')
        )
        OrderItem.objects.create(
            order=self.order, menu_item=self.item, item_name="Margherita", 
            item_price=10, quantity=1, subtotal=10
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_filter_orders_by_status(self):
        # Create another order with a different status
        Order.objects.create(customer=self.customer, restaurant=self.restaurant, status='DELIVERED', total_amount=15)
        
        # Fetch only PLACED orders
        response = self.client.get('/api/v1/orders/?status=PLACED')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['status'], 'PLACED')

    def test_update_order_status(self):
        url = f'/api/v1/orders/{self.order.id}/update-status/'
        # Change status to CONFIRMED to trigger the confirmed_at timestamp
        response = self.client.post(url, {"status": "CONFIRMED"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CONFIRMED')
        self.assertIsNotNone(self.order.confirmed_at) # Check if timestamp was set by update_status method
    def test_cancel_order(self):
        url = f'/api/v1/orders/{self.order.id}/cancel/'
        response = self.client.post(url, {"reason": "Out of stock"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CANCELLED')
        self.assertEqual(self.order.cancellation_reason, 'Out of stock')

    def test_cannot_cancel_delivered_order(self):
        self.order.status = 'DELIVERED'
        self.order.save()
        
        url = f'/api/v1/orders/{self.order.id}/cancel/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)