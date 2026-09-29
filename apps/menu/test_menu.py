from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
import decimal

class MenuTests(APITestCase):
    def setUp(self):
        # Create Restaurant
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        # Create Category
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant, name="Pizzas", is_active=True
        )
        
        # Create Menu Items
        self.item1 = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Margherita", 
            description="Classic", price=decimal.Decimal('10.00'), is_available=True, 
            is_featured=True, is_new=True, rating=4.5
        )
        self.item2 = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Pepperoni", 
            description="Meaty", price=decimal.Decimal('12.00'), is_available=True, 
            is_featured=False, is_new=False, rating=4.8
        )
        # Unavailable item (should not show in lists)
        self.item3 = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Out of Stock", 
            description="Hidden", price=decimal.Decimal('15.00'), is_available=False
        )

    def test_list_menu_items(self):
        response = self.client.get('/api/v1/menu/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 2 (excludes item3 which is unavailable)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_new_items(self):
        response = self.client.get('/api/v1/menu/items/?is_new=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Margherita")

    def test_recommended_items(self):
        response = self.client.get('/api/v1/menu/items/recommended/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include item1 (featured) and item2 (rating >= 4.0)
        self.assertEqual(len(response.data), 2)

    def test_menu_item_detail(self):
        url = f'/api/v1/menu/items/{self.item1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Margherita")
        self.assertIn('customizations', response.data)
        self.assertIn('add_ons', response.data)

    def test_category_items(self):
        url = f'/api/v1/menu/categories/{self.category.id}/items/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)