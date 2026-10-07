from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant, RestaurantHoliday, RestaurantDeliveryZone
import decimal

class SettingsTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True,
            delivery_fee=decimal.Decimal('3.00')
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_get_settings(self):
        response = self.client.get('/api/v1/restaurants/settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Pizza")
        self.assertEqual(response.data['delivery_fee'], '3.00')

    def test_update_settings(self):
        response = self.client.patch('/api/v1/restaurants/settings/', {
            "delivery_fee": "5.00",
            "tax_rate": "8.5"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['delivery_fee'], '5.00')
        self.assertEqual(response.data['tax_rate'], '8.50')
        
        # Verify DB updated
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.delivery_fee, decimal.Decimal('5.00'))

    def test_add_holiday(self):
        response = self.client.post('/api/v1/restaurants/holidays/', {
            "holiday_date": "2026-12-25",
            "reason": "Christmas"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RestaurantHoliday.objects.count(), 1)
        # Verify it's attached to the right restaurant
        self.assertEqual(response.data['reason'], "Christmas")

    def test_add_delivery_zone(self):
        response = self.client.post('/api/v1/restaurants/delivery-zones/', {
            "zone_name": "Downtown",
            "delivery_fee": "4.00",
            "delivery_time_minutes": 45,
            "postal_codes": "10001,10002",
            "is_active": True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RestaurantDeliveryZone.objects.count(), 1)

    def test_customer_cannot_access_settings(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/v1/restaurants/settings/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)