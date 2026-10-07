from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem
import decimal

class DashboardTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        self.category = MenuCategory.objects.create(restaurant=self.restaurant, name="Pizzas")
        self.item1 = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Margherita", 
            description="Cheese", price=decimal.Decimal('10.00'), is_available=True
        )
        self.item2 = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Pepperoni", 
            description="Meat", price=decimal.Decimal('12.00'), is_available=True
        )
        
        # Create some orders
        self.order1 = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='PICKUP', 
            status='DELIVERED', payment_status='COMPLETED', total_amount=decimal.Decimal('22.00')
        )
        OrderItem.objects.create(order=self.order1, menu_item=self.item1, item_name="Margherita", item_price=10, quantity=1, subtotal=10)
        OrderItem.objects.create(order=self.order1, menu_item=self.item2, item_name="Pepperoni", item_price=12, quantity=1, subtotal=12)
        
        self.order2 = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='DELIVERY', 
            status='PLACED', payment_status='PENDING', total_amount=decimal.Decimal('10.00')
        )
        OrderItem.objects.create(order=self.order2, menu_item=self.item1, item_name="Margherita", item_price=10, quantity=1, subtotal=10)
        
        self.client.force_authenticate(user=self.owner)

    def test_dashboard_overview(self):
        response = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['restaurant_name'], "Test Pizza")
        self.assertEqual(response.data['total_orders'], 2)
        self.assertEqual(response.data['total_sales'], '32.00')
        self.assertEqual(response.data['total_customers'], 1) # Both orders by same customer

    def test_popular_items(self):
        response = self.client.get('/api/v1/analytics/dashboard/popular_items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Margherita was ordered twice, Pepperoni once
        self.assertEqual(response.data[0]['name'], "Margherita")
        self.assertEqual(response.data[0]['total_quantity_sold'], 2)
        self.assertEqual(response.data[1]['name'], "Pepperoni")
        self.assertEqual(response.data[1]['total_quantity_sold'], 1)

    def test_recent_orders(self):
        response = self.client.get('/api/v1/analytics/dashboard/recent_orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # order2 was placed after order1, so it should be first
        self.assertEqual(response.data[0]['status'], 'PLACED')

    def test_customer_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/v1/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)