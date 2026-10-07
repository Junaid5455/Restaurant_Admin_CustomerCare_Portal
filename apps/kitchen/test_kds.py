from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant, RestaurantStaffMember
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem
import decimal

class KitchenTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.staff_user = User.objects.create_user(email='staff@test.com', password='pass1234', role='RESTAURANT_STAFF')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        # Assign staff to restaurant
        RestaurantStaffMember.objects.create(
            user=self.staff_user, restaurant=self.restaurant, role='KITCHEN_STAFF'
        )
        
        self.category = MenuCategory.objects.create(restaurant=self.restaurant, name="Pizzas")
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Margherita", 
            description="Cheese", price=decimal.Decimal('10.00'), is_available=True
        )
        
        # Create a confirmed order for the kitchen
        self.order1 = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='PICKUP', 
            status='CONFIRMED', payment_status='COMPLETED', total_amount=decimal.Decimal('10.50')
        )
        OrderItem.objects.create(
            order=self.order1, menu_item=self.item, item_name="Margherita", 
            item_price=10, quantity=2, subtotal=20
        )
        
        # Create a preparing order
        self.order2 = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='DINE_IN', 
            status='PREPARING', payment_status='COMPLETED', total_amount=decimal.Decimal('10.50'),
            table_number="12A"
        )
        OrderItem.objects.create(
            order=self.order2, menu_item=self.item, item_name="Margherita", 
            item_price=10, quantity=1, subtotal=10
        )
        
        # Create a placed order (should NOT show on KDS)
        self.order3 = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='PICKUP', 
            status='PLACED', payment_status='PENDING', total_amount=decimal.Decimal('10.50')
        )

    def test_staff_can_list_kitchen_orders(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get('/api/v1/kitchen/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return order1 and order2 (CONFIRMED and PREPARING)
        self.assertEqual(len(response.data), 2)

    def test_start_preparation(self):
        self.client.force_authenticate(user=self.staff_user)
        url = f'/api/v1/kitchen/orders/{self.order1.id}/start/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'PREPARING')

    def test_mark_ready(self):
        self.client.force_authenticate(user=self.staff_user)
        url = f'/api/v1/kitchen/orders/{self.order2.id}/ready/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order2.refresh_from_db()
        self.assertEqual(self.order2.status, 'READY')

    def test_customer_cannot_access_kds(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/v1/kitchen/orders/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)