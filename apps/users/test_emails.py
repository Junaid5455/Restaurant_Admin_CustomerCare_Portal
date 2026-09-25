from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, EmailVerificationToken, PasswordResetToken
from django.core import mail
from django.utils import timezone
from datetime import timedelta

class EmailVerificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', password='StrongPassword123!', role='CUSTOMER'
        )
        self.send_url = reverse('send_verification')
        self.verify_url = reverse('verify_email')

    def test_send_verification_email(self):
        response = self.client.post(self.send_url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Verify your email address', mail.outbox[0].subject)

    def test_verify_email_with_valid_token(self):
        token = EmailVerificationToken.create_for_user(self.user)
        response = self.client.post(self.verify_url, {'token': token.token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_verify_email_with_expired_token(self):
        token = EmailVerificationToken.create_for_user(self.user)
        token.expires_at = timezone.now() - timedelta(days=1)
        token.save()
        
        response = self.client.post(self.verify_url, {'token': token.token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', password='StrongPassword123!', role='CUSTOMER'
        )
        self.forgot_url = reverse('forgot_password')
        self.reset_url = reverse('reset_password')

    def test_request_password_reset(self):
        response = self.client.post(self.forgot_url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset your password', mail.outbox[0].subject)

    def test_reset_password_with_valid_token(self):
        token = PasswordResetToken.create_for_user(self.user)
        data = {
            'token': token.token,
            'new_password': 'NewStrongPassword123!',
            'new_password_confirm': 'NewStrongPassword123!'
        }
        response = self.client.post(self.reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1) # Password changed email sent
        
        # Check if password actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPassword123!'))

    def test_reset_password_with_mismatched_passwords(self):
        token = PasswordResetToken.create_for_user(self.user)
        data = {
            'token': token.token,
            'new_password': 'NewStrongPassword123!',
            'new_password_confirm': 'DifferentPassword123!'
        }
        response = self.client.post(self.reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_invalidates_token(self):
        token = PasswordResetToken.create_for_user(self.user)
        data = {
            'token': token.token,
            'new_password': 'NewStrongPassword123!',
            'new_password_confirm': 'NewStrongPassword123!'
        }
        self.client.post(self.reset_url, data, format='json')
        
        token.refresh_from_db()
        self.assertTrue(token.is_used)