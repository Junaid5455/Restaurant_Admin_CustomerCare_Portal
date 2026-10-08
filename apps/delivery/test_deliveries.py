from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant, RestaurantStaffMember
from apps.orders.models import Order
from apps.delivery.models import Delivery
import decimal

class DeliveryTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.driver_user = User.objects.create_user(email='driver@test.com', password='pass1234', role='DELIVERY_STAFF')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True, allows_delivery=True
        )
        
        # Create a driver staff member
        self.driver = RestaurantStaffMember.objects.create(
            user=self.driver_user, restaurant=self.restaurant, role='DELIVERY_STAFF'
        )
        
        # Create a delivery order
        self.order = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='DELIVERY', 
            status='READY', payment_status='COMPLETED', total_amount=decimal.Decimal('15.00'),
            delivery_address="456 Cust St"
        )
        
        # Create the Delivery object
        self.delivery = Delivery.objects.create(
            order=self.order, customer=self.customer, restaurant=self.restaurant,
            pickup_address="123 St", delivery_address="456 Cust St",
            estimated_delivery_time_minutes=30, status='PENDING'
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_assign_driver(self):
        url = f'/api/v1/delivery/{self.delivery.id}/assign-driver/'
        response = self.client.post(url, {"driver_id": str(self.driver.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, 'ASSIGNED')
        self.assertEqual(self.delivery.driver, self.driver)
        self.assertIsNotNone(self.delivery.assigned_at)

    def test_driver_views_assigned_deliveries(self):
        # Assign driver first
        self.delivery.assign_driver(self.driver)
        
        self.client.force_authenticate(user=self.driver_user)
        response = self.client.get('/api/v1/delivery/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['status'], 'ASSIGNED')

    def test_update_location(self):
        self.delivery.assign_driver(self.driver)
        
        self.client.force_authenticate(user=self.driver_user)
        url = f'/api/v1/delivery/{self.delivery.id}/update-location/'
        response = self.client.post(url, {
            "latitude": "40.712776",
            "longitude": "-74.005974"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.delivery.refresh_from_db()
        self.assertEqual(str(self.delivery.current_latitude), '40.712776')
        self.assertIsNotNone(self.delivery.last_location_update)

    def test_mark_picked_up_and_delivered(self):
        self.delivery.assign_driver(self.driver)
        
        self.client.force_authenticate(user=self.driver_user)
        
        # 1. Mark picked up
        url_pickup = f'/api/v1/delivery/{self.delivery.id}/mark-picked-up/'
        response = self.client.post(url_pickup, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, 'PICKED_UP')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'OUT_FOR_DELIVERY') # Order status updated
        
        # 2. Mark delivered
        url_delivered = f'/api/v1/delivery/{self.delivery.id}/mark-delivered/'
        response = self.client.post(url_delivered, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, 'DELIVERED')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'DELIVERED') # Order status updated