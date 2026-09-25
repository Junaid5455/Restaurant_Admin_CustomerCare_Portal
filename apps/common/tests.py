from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order
import decimal
from django.utils import timezone

class RBACTests(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.admin = User.objects.create_user(email='admin@test.com', password='pass1234', role='SUPER_ADMIN')
        self.owner1 = User.objects.create_user(email='owner1@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.owner2 = User.objects.create_user(email='owner2@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='customer@test.com', password='pass1234', role='CUSTOMER')
        
        # Create restaurant for owner1
        self.restaurant1 = Restaurant.objects.create(
            owner=self.owner1, name="Owner1 Pizza", email="o1@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00"
        )
        
        # Create restaurant for owner2
        self.restaurant2 = Restaurant.objects.create(
            owner=self.owner2, name="Owner2 Burgers", email="o2@test.com", phone="456",
            address="456 Ave", city="LA", state="CA", country="USA", postal_code="90001",
            opening_time="09:00:00", closing_time="22:00:00"
        )

    def test_anonymous_cannot_create_restaurant(self):
        response = self.client.post('/api/v1/restaurants/', {
            'name': 'Test', 'email': 'test@test.com', 'phone': '123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_cannot_create_restaurant(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/v1/restaurants/', {
            'name': 'Test', 'email': 'test@test.com', 'phone': '123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_create_restaurant(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.post('/api/v1/restaurants/', {
            'name': 'New Pizza', 'email': 'new@test.com', 'phone': '123',
            'address': '123 St', 'city': 'NY', 'state': 'NY', 'country': 'USA', 'postal_code': '10001',
            'opening_time': '09:00:00', 'closing_time': '22:00:00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_owner_cannot_modify_other_restaurant(self):
        self.client.force_authenticate(user=self.owner1)
        url = f'/api/v1/restaurants/{self.restaurant2.id}/'
        response = self.client.patch(url, {'name': 'Hacked Burgers'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_modify_any_restaurant(self):
        self.client.force_authenticate(user=self.admin)
        url = f'/api/v1/restaurants/{self.restaurant1.id}/'
        response = self.client.patch(url, {'name': 'Admin Updated Pizza'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_queryset_filtering_for_restaurants(self):
        self.client.force_authenticate(user=self.owner1)
        response = self.client.get('/api/v1/restaurants/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # The CustomPagination wraps the list inside a 'data' key
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Owner1 Pizza")