from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
import decimal

class RestaurantBrowseTests(APITestCase):
    def setUp(self):
        # Create Customers
        self.customer = User.objects.create_user(email='customer@test.com', password='pass1234', role='CUSTOMER')
        
        # Create Owner & Restaurant
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True, allows_delivery=True
        )
        
        # Create Inactive Restaurant (should not be visible to customers)
        self.inactive_restaurant = Restaurant.objects.create(
            owner=self.owner, name="Closed Pizza", email="c@test.com", phone="456",
            address="456 Ave", city="LA", state="CA", country="USA", postal_code="90001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=False
        )
        
        # Create Menu Data
        self.category = MenuCategory.objects.create(restaurant=self.restaurant, name="Pizzas", is_active=True)
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Margherita", 
            description="Classic", price=decimal.Decimal('10.00'), is_available=True, is_featured=True
        )

    def test_list_restaurants_active_only(self):
        response = self.client.get('/api/v1/restaurants/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Test Pizza")

    def test_search_restaurants(self):
        response = self.client.get('/api/v1/restaurants/search/?q=Pizza')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_restaurant_menu_action(self):
        url = f'/api/v1/restaurants/{self.restaurant.id}/menu/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Pizzas")
        self.assertEqual(len(response.data[0]['items']), 1)

    def test_list_menu_items(self):
        response = self.client.get('/api/v1/menu/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Margherita")

    def test_menu_item_detail(self):
        url = f'/api/v1/menu/items/{self.item.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Margherita")
        self.assertIn('customizations', response.data)