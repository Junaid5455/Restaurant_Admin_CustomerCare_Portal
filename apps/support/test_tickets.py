from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.orders.models import Order
from apps.support.models import SupportTicket
import decimal

class SupportTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        # Create a dummy order to attach to the ticket
        self.order = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='PICKUP', 
            status='DELIVERED', payment_status='COMPLETED', 
            total_amount=decimal.Decimal('10.50')
        )
        
        self.client.force_authenticate(user=self.customer)

    def test_create_ticket(self):
        response = self.client.post('/api/v1/support/tickets/', {
            "restaurant": str(self.restaurant.id),
            "related_order": str(self.order.id),
            "subject": "Missing item",
            "description": "I didn't get my coke",
            "category": "MISSING_ITEMS",
            "priority": "HIGH"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_email'], 'cust@test.com')
        self.assertEqual(response.data['status'], 'OPEN')
        # Ensure a ticket_id was auto-generated
        self.assertIsNotNone(response.data['ticket_id'])

    def test_add_message_to_ticket(self):
        ticket = SupportTicket.objects.create(
            customer=self.customer, restaurant=self.restaurant, subject="Late delivery", 
            description="Food is cold", category="DELIVERY_ISSUE"
        )
        
        url = f'/api/v1/support/tickets/{ticket.id}/add_message/'
        response = self.client.post(url, {"message": "Hello, anyone there?"}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender_email'], 'cust@test.com')
        self.assertEqual(response.data['message_type'], 'CUSTOMER_MESSAGE')

    def test_close_ticket(self):
        ticket = SupportTicket.objects.create(
            customer=self.customer, restaurant=self.restaurant, subject="Refund", 
            description="Please refund me", category="REFUND_REQUEST"
        )
        
        url = f'/api/v1/support/tickets/{ticket.id}/close/'
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'CLOSED')
        self.assertTrue(ticket.is_resolved)

    def test_owner_can_view_tickets(self):
        SupportTicket.objects.create(
            customer=self.customer, restaurant=self.restaurant, subject="Test", 
            description="Desc", category="OTHER"
        )
        
        # Log in as owner
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/v1/support/tickets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
    