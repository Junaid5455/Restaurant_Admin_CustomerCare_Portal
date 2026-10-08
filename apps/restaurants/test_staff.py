from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant, RestaurantStaffMember

class StaffTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_create_new_staff_account(self):
        response = self.client.post('/api/v1/restaurants/staff/', {
            "staff_email": "newstaff@test.com",
            "role": "KITCHEN_STAFF",
            "can_manage_orders": True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if a new user was created with the correct role
        user = User.objects.get(email="newstaff@test.com")
        self.assertEqual(user.role, 'RESTAURANT_STAFF')
        
        # Check if they were linked to the restaurant
        self.assertEqual(RestaurantStaffMember.objects.count(), 1)

    def test_add_existing_customer_as_staff(self):
        # Customer already exists
        response = self.client.post('/api/v1/restaurants/staff/', {
            "staff_email": "cust@test.com",
            "role": "CASHIER"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Ensure their role was upgraded from CUSTOMER to RESTAURANT_STAFF
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role, 'RESTAURANT_STAFF')

    def test_toggle_staff_active(self):
        staff_user = User.objects.create_user(email='staff@test.com', password='pass1234', role='RESTAURANT_STAFF')
        staff = RestaurantStaffMember.objects.create(user=staff_user, restaurant=self.restaurant, role='CASHIER')
        
        url = f'/api/v1/restaurants/staff/{staff.id}/toggle-active/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        staff.refresh_from_db()
        self.assertFalse(staff.is_active) # Was True, should now be False

    def test_update_permissions(self):
        staff_user = User.objects.create_user(email='staff@test.com', password='pass1234', role='RESTAURANT_STAFF')
        staff = RestaurantStaffMember.objects.create(user=staff_user, restaurant=self.restaurant, role='MANAGER')
        
        url = f'/api/v1/restaurants/staff/{staff.id}/update-permissions/'
        response = self.client.post(url, {
            "can_manage_menu": True,
            "can_view_analytics": True
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        staff.refresh_from_db()
        self.assertTrue(staff.can_manage_menu)
        self.assertTrue(staff.can_view_analytics)
        self.assertFalse(staff.can_manage_staff) # Should remain False as we didn't send it