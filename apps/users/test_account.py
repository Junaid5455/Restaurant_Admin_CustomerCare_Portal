from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, UserProfile, FavoriteRestaurant, GiftCard
from apps.restaurants.models import Restaurant
import decimal

class AccountTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(email='cust@test.com', password='pass1234', role='CUSTOMER')
        self.owner = User.objects.create_user(email='owner@test.com', password='pass1234', role='RESTAURANT_OWNER')
        
        self.restaurant = Restaurant.objects.create(
            owner=self.owner, name="Test Pizza", email="r@test.com", phone="123",
            address="123 St", city="NY", state="NY", country="USA", postal_code="10001",
            opening_time="09:00:00", closing_time="22:00:00", is_active=True
        )
        
        self.client.force_authenticate(user=self.customer)

    def test_view_rewards(self):
        # Ensure profile exists and update points
        profile, _ = UserProfile.objects.get_or_create(user=self.customer)
        profile.loyalty_points = 150
        profile.total_orders = 5
        profile.save()

        response = self.client.get('/api/v1/users/rewards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loyalty_points'], 150)
        self.assertEqual(response.data['total_orders'], 5)

    def test_add_favorite_restaurant(self):
        response = self.client.post('/api/v1/users/favorites/restaurants/', {
            "restaurant_id": str(self.restaurant.id)
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteRestaurant.objects.count(), 1)
        # Verify it returns the nested restaurant data
        self.assertEqual(response.data['restaurant']['name'], "Test Pizza")

    def test_remove_favorite_restaurant(self):
        fav = FavoriteRestaurant.objects.create(user=self.customer, restaurant=self.restaurant)
        response = self.client.delete(f'/api/v1/users/favorites/restaurants/{fav.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteRestaurant.objects.count(), 0)

    def test_view_gift_cards(self):
        GiftCard.objects.create(
            user=self.customer, code="GIFT123", initial_amount=decimal.Decimal('50.00'),
            balance=decimal.Decimal('25.00')
        )
        response = self.client.get('/api/v1/users/gift-cards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Our CustomPagination wraps the list inside a 'data' key
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['balance'], '25.00')