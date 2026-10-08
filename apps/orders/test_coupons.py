from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.orders.models import Coupon
from django.utils import timezone
from datetime import timedelta
import decimal

class CouponTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        self.coupon = Coupon.objects.create(
            restaurant=self.restaurant, code="SAVE10",
            discount_type='PERCENTAGE', discount_value=decimal.Decimal('10.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=1),
            is_active=True, max_uses=100
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_create_coupon(self):
        # Updated URL path
        response = self.client.post('/api/v1/orders/coupons/', {
            "restaurant_id": str(self.restaurant.id),
            "code": "SUMMER5",
            "discount_type": "FIXED",
            "discount_value": "5.00",
            "valid_from": timezone.now().isoformat(),
            "valid_to": (timezone.now() + timedelta(days=30)).isoformat()
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], "SUMMER5")
        self.assertEqual(Coupon.objects.count(), 2)

    def test_create_duplicate_coupon_fails(self):
        # Updated URL path
        response = self.client.post('/api/v1/orders/coupons/', {
            "restaurant_id": str(self.restaurant.id),
            "code": "SAVE10", # Already exists
            "discount_type": "PERCENTAGE",
            "discount_value": "20.00",
            "valid_from": timezone.now().isoformat(),
            "valid_to": (timezone.now() + timedelta(days=30)).isoformat()
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_toggle_coupon_active(self):
        # Updated URL path
        url = f'/api/v1/orders/coupons/{self.coupon.id}/toggle-active/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.coupon.refresh_from_db()
        self.assertFalse(self.coupon.is_active)

    def test_customer_cannot_create_coupon(self):
        self.client.force_authenticate(user=self.customer)
        # Updated URL path
        response = self.client.post('/api/v1/orders/coupons/', {
            "restaurant_id": str(self.restaurant.id),
            "code": "HACKED",
            "discount_type": "PERCENTAGE",
            "discount_value": "99.00",
            "valid_from": timezone.now().isoformat(),
            "valid_to": (timezone.now() + timedelta(days=30)).isoformat()
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)