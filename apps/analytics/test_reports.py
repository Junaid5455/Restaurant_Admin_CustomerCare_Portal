from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem
import decimal

class ReportTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        # Create a delivered order
        self.order = Order.objects.create(
            customer=self.customer, restaurant=self.restaurant, order_type='PICKUP', 
            status='DELIVERED', payment_status='COMPLETED', total_amount=decimal.Decimal('15.00')
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_sales_report(self):
        response = self.client.get('/api/v1/analytics/dashboard/sales-report/?period=daily')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Should have at least 1 day with data
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[-1]['total_orders'], 1)
        self.assertEqual(response.data[-1]['total_sales'], '15.00')

    def test_customer_analytics(self):
        response = self.client.get('/api/v1/analytics/dashboard/customer-analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['customer_email'], 'cust@test.com')
        self.assertEqual(response.data[0]['total_spent'], '15.00')

    def test_operational_metrics(self):
        response = self.client.get('/api/v1/analytics/dashboard/operational-metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_export_sales_csv(self):
        response = self.client.get('/api/v1/analytics/dashboard/export-sales/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="sales_report_Test Pizza.csv"', response['Content-Disposition'])
        
        # Check if CSV contains the order number
        content = response.content.decode('utf-8')
        self.assertIn(self.order.order_number, content)