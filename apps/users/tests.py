from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.me_url = reverse('current_user')
        self.refresh_url = reverse('token_refresh')
        self.logout_url = reverse('logout')
        self.change_password_url = reverse('change_password')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': 'CUSTOMER'
        }
        
    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertIn('access_token', response.data['data'])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_duplicate_email_registration(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_password_mismatch(self):
        data = self.user_data.copy()
        data['password_confirm'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data['errors'])

    def test_user_login(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'StrongPassword123!'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data['data'])

    def test_login_wrong_password(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'WrongPassword123!'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'StrongPassword123!'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['data']['access_token']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], 'test@example.com')

    def test_change_password(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'StrongPassword123!'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['data']['access_token']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        change_data = {
            'old_password': 'StrongPassword123!',
            'new_password': 'NewStrongPassword123!',
            'new_password_confirm': 'NewStrongPassword123!'
        }
        response = self.client.post(self.change_password_url, change_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': 'test@example.com', 'password': 'StrongPassword123!'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['data']['refresh_token']
        
        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)