from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.orders.models import Order
import decimal

class SuperAdminTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.com', password='pass1234', role='SUPER_ADMIN', is_staff=True, is_superuser=True)
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, status='DELIVERED', 
            total_amount=decimal.Decimal('50.00')
        )
        
        self.client.force_authenticate(user=self.admin)

    def test_dashboard_stats(self):
        response = self.client.get('/api/v1/admin/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_revenue'], '50.00')
        self.assertEqual(response.data['active_restaurants'], 1)
        self.assertEqual(response.data['total_customers'], 1)

    def test_list_users(self):
        response = self.client.get('/api/v1/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3) # admin, customer, owner

    def test_toggle_user_active(self):
        # Updated URL path to match DRF routing
        url = '/api/v1/admin/{}/toggle-user-active/'.format(self.customer.id)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active) # Should be blocked now

    def test_toggle_restaurant_active(self):
        # Updated URL path to match DRF routing
        url = '/api/v1/admin/{}/toggle-restaurant-active/'.format(self.restaurant.id)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.restaurant.refresh_from_db()
        self.assertFalse(self.restaurant.is_active) # Should be deactivated now

    def test_list_orders(self):
        response = self.client.get('/api/v1/admin/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['total_amount'], '50.00')

    def test_non_admin_cannot_access(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/v1/admin/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)