from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant, RestaurantTable, Reservation
from django.utils import timezone
from datetime import timedelta

class ReservationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True, allows_dine_in=True
        )
        
        self.table = RestaurantTable.objects.create(
            restaurant=self.restaurant, table_number="1", capacity=4
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_create_table_and_qr_code(self):
        # Updated URL path
        response = self.client.post('/api/v1/restaurants/tables/', {
            "table_number": "2",
            "capacity": 2
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Ensure QR token is auto-generated
        self.assertIsNotNone(response.data['qr_code_token'])

    def test_customer_creates_reservation(self):
        self.client.force_authenticate(user=self.customer)
        # Updated URL path
        response = self.client.post('/api/v1/restaurants/reservations/', {
            "restaurant": str(self.restaurant.id),
            "reservation_time": (timezone.now() + timedelta(days=2)).isoformat(),
            "party_size": 3,
            "special_requests": "Window seat please"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['customer_email'], 'cust@test.com')

    def test_check_available_slots(self):
        self.client.force_authenticate(user=self.customer)
        date_str = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        # Updated URL path
        url = f'/api/v1/restaurants/reservations/available-slots/?restaurant_id={self.restaurant.id}&date={date_str}'
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return slots between 09:00 and 22:00
        self.assertEqual(len(response.data), 13)
        self.assertTrue(response.data[0]['is_available'])

    def test_confirm_reservation(self):
        reservation = Reservation.objects.create(
            customer=self.customer, restaurant=self.restaurant, 
            reservation_time=timezone.now() + timedelta(days=2), party_size=2
        )
        
        # Updated URL path
        url = f'/api/v1/restaurants/reservations/{reservation.id}/confirm/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'CONFIRMED')

    def test_customer_cancels_reservation(self):
        self.client.force_authenticate(user=self.customer)
        reservation = Reservation.objects.create(
            customer=self.customer, restaurant=self.restaurant, 
            reservation_time=timezone.now() + timedelta(days=2), party_size=2
        )
        
        # Updated URL path
        url = f'/api/v1/restaurants/reservations/{reservation.id}/cancel/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'CANCELLED')