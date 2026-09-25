"""
ASGI configuration for the Restaurant Portal project.

Currently uses Django's standard ASGI application. When WebSocket
support is added in later steps, this will be replaced with a
Channels ProtocolTypeRouter configuration.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "restaurant_portal.settings.development",
)

application = get_asgi_application()