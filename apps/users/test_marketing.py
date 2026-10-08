from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, NotificationPreference, Campaign, Notification
from apps.restaurants.models import Restaurant
import decimal

class MarketingTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        self.customer1 = User.objects.create_user(email='cust1@test.com', password='pass1234', role='CUSTOMER')
        self.customer2 = User.objects.create_user(email='cust2@test.com', password='pass1234', role='CUSTOMER')
        
        # Set preferences for customer 1 (opted in to email promos)
        NotificationPreference.objects.create(user=self.customer1, email_promotions=True)
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        self.campaign = Campaign.objects.create(
            restaurant=self.restaurant, name="Summer Sale", channel='EMAIL', 
            target_segment='ALL', subject="20% Off!", body="Get 20% off your next order."
        )
        
        self.client.force_authenticate(user=self.owner)

    def test_create_campaign(self):
        response = self.client.post('/api/v1/users/campaigns/', {
            "restaurant_id": str(self.restaurant.id),
            "name": "Winter Promo",
            "channel": "EMAIL",
            "target_segment": "ALL",
            "subject": "Stay warm with us!",
            "body": "Hot soup deals inside."
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_send_campaign(self):
        url = f'/api/v1/users/campaigns/{self.campaign.id}/send/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only send to customer 1 (who opted in)
        self.assertEqual(response.data['recipient_count'], 1)
        
        # Check if notification was created for customer 1
        self.assertEqual(Notification.objects.filter(user=self.customer1).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.customer2).count(), 0)
        
        self.campaign.refresh_from_db()
        self.assertTrue(self.campaign.is_sent)

    def test_customer_sets_preferences(self):
        self.client.force_authenticate(user=self.customer2)
        response = self.client.post('/api/v1/users/preferences/', {
            "email_promotions": True,
            "sms_promotions": False
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Update existing preference
        response = self.client.patch(f'/api/v1/users/preferences/{response.data["id"]}/', {
            "sms_promotions": True
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['sms_promotions'])