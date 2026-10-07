from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
import decimal

class MenuManagementTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        self.category = MenuCategory.objects.create(restaurant=self.restaurant, name="Pizzas", is_active=True)
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Margherita", 
            description="Cheese", price=decimal.Decimal('10.00'), is_available=True
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_create_menu_category(self):
        response = self.client.post('/api/v1/menu/categories/', {
            "restaurant_id": str(self.restaurant.id),
            "name": "Sides",
            "is_active": True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuCategory.objects.count(), 2)

    def test_update_menu_item(self):
        url = f'/api/v1/menu/items/{self.item.id}/'
        response = self.client.patch(url, {
            "price": "12.50",
            "is_featured": True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.price, decimal.Decimal('12.50'))
        self.assertTrue(self.item.is_featured)

    def test_toggle_availability(self):
        url = f'/api/v1/menu/items/{self.item.id}/toggle_availability/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertFalse(self.item.is_available) # Was True, should now be False

    def test_customer_cannot_create_item(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/v1/menu/items/', {
            "category_id": str(self.category.id),
            "name": "Pepperoni",
            "price": "15.00"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_manage_other_restaurant_item(self):
        # Create another owner and restaurant
        owner2 = User.objects.create_user(email='owner2@test.com', password='pass1234', role='RESTAURANT_OWNER')
        restaurant2 = Restaurant.objects.create(
            owner=owner2, name="Burger Stand", email="b@test.com", phone="456",
            address="456 Ave", city="LA", state="CA", country="USA", postal_code="90001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        cat2 = MenuCategory.objects.create(restaurant=restaurant2, name="Burgers")
        
        # Owner 1 tries to update Owner 2's category
        url = f'/api/v1/menu/categories/{cat2.id}/'
        response = self.client.patch(url, {"name": "Hacked Burgers"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)