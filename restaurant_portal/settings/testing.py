"""
Testing-specific settings.

- In-memory SQLite database
- Disabled migrations for speed
- Console email backend
- Fast password hashing
"""
import tempfile
from .base import *  # noqa: F401, F403

# ====================================================
# Debug Mode
# ====================================================
DEBUG = False
ALLOWED_HOSTS = ["*"]

# ====================================================
# Use SQLite in-memory for fast tests
# ====================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ====================================================
# Disable migrations for faster test runs
# ====================================================
class DisableMigrations:
    """Disable migrations during testing — models created directly."""

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# ====================================================
# Password Hashers - Use MD5 for speed in tests
# ====================================================
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ====================================================
# Disable password validators
# ====================================================
AUTH_PASSWORD_VALIDATORS = []  # noqa: F405

# ====================================================
# Email Backend — Use in-memory for tests
# ====================================================
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "test@restaurantportal.com"

# ====================================================
# Cache — Use in-memory for tests
# ====================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# ====================================================
# Media files — use temporary directory for tests
# ====================================================
MEDIA_ROOT = tempfile.mkdtemp()

# ====================================================
# Celery — Run tasks eagerly during tests
# ====================================================
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"

# ====================================================
# Channels — Use in-memory channel layer for tests
# ====================================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# ====================================================
# Logging — Reduce verbosity during tests
# ====================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["null"], "level": "CRITICAL", "propagate": False},
        "apps": {"handlers": ["null"], "level": "CRITICAL", "propagate": False},
        "celery": {"handlers": ["null"], "level": "CRITICAL", "propagate": False},
    },
}

# ====================================================
# Disable throttling during tests
# ====================================================
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405