"""
Pytest configuration and shared fixtures for the Restaurant Portal.
"""
import pytest
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.fixture
def user_factory(db):
    """Factory fixture for creating test users."""
    from factory import Factory, Faker, SubFactory
    from factory.django import DjangoModelFactory

    class UserFactory(DjangoModelFactory):
        class Meta:
            model = User

        email = Faker("email")
        first_name = Faker("first_name")
        last_name = Faker("last_name")
        password = "testpass123"

    return UserFactory


@pytest.fixture
def admin_user(db):
    """Create and return a superuser for testing."""
    return User.objects.create_superuser(
        email="admin@test.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def api_client():
    """Return an unauthenticated DRF API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Return an authenticated DRF API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client