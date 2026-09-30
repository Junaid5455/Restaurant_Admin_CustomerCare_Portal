from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, SavedAddress
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
import decimal # Make sure to import decimal

class OrderTypeTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Pizza Place", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True, 
            tax_rate=decimal.Decimal('5.00'), delivery_fee=decimal.Decimal('3.00'),
            allows_pickup=True, allows_delivery=True, allows_dine_in=True
        )
        
        self.category = MenuCategory.objects.create(restaurant=self.restaurant, name="Pizzas")
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Margherita", 
            description="Cheese", price=decimal.Decimal('10.00'), is_available=True
        )
        
        self.address = SavedAddress.objects.create(
            user=self.customer, label="Home", address="456 Main St", city="NY", 
            state="NY", country="USA", postal_code="10002", is_default=True
        )
        
        self.client.force_authenticate(user=self.customer)
        
        # Add item to cart first
        self.client.post('/api/v1/orders/cart/items/', {
            "menu_item_id": str(self.item.id), "quantity": 1
        }, format='json')

    def test_delivery_order_flow(self):
        response = self.client.post('/api/v1/orders/cart/checkout/', {
            "order_type": "DELIVERY",
            "address_id": str(self.address.id),
            "delivery_instructions": "Leave at door"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_type'], "DELIVERY")
        # Compare as Decimal objects to handle trailing zeros
        self.assertEqual(decimal.Decimal(response.data['total_amount']), decimal.Decimal('13.50'))

    def test_pickup_order_flow(self):
        response = self.client.post('/api/v1/orders/cart/checkout/', {
            "order_type": "PICKUP",
            "pickup_time": "2026-10-01T18:00:00Z"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_type'], "PICKUP")
        # Compare as Decimal objects to handle trailing zeros
        self.assertEqual(decimal.Decimal(response.data['total_amount']), decimal.Decimal('10.50'))

    def test_dine_in_order_flow(self):
        response = self.client.post('/api/v1/orders/cart/checkout/', {
            "order_type": "DINE_IN",
            "table_number": "12A",
            "number_of_guests": 4
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_type'], "DINE_IN")

    def test_delivery_missing_address_validation(self):
        response = self.client.post('/api/v1/orders/cart/checkout/', {
            "order_type": "DELIVERY"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_id", response.data)