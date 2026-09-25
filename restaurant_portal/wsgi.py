"""
WSGI configuration for the Restaurant Portal project.
"""
import os

from django.core.wsgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "restaurant_portal.settings.development",
)

application = get_asgi_application()