"""
Development-specific settings.

- DEBUG = True
- Django Debug Toolbar enabled
- Relaxed security settings
- Console email backend
"""
import sys
from .base import *  # noqa: F401, F403
from .base import BASE_DIR, env

# ====================================================
# Test Environment Detection
# ====================================================
TESTING = 'test' in sys.argv

# ====================================================
# Debug Mode
# ====================================================
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ====================================================
# Additional Development Apps & Middleware (Skip during tests)
# ====================================================
if not TESTING:
    INSTALLED_APPS += [  # noqa: F405
        "debug_toolbar",
    ]

    # Debug Toolbar Middleware (must be early)
    MIDDLEWARE = [  # noqa: F405
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

# ====================================================
# Debug Toolbar Configuration
# ====================================================
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True,
    'IS_RUNNING_TESTS': False,  # Fixes the test runner error
}

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]

# ====================================================
# Use console email for development
# ====================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ====================================================
# Disable password validation in development for speed
# ====================================================
AUTH_PASSWORD_VALIDATORS = []  # noqa: F405

# ====================================================
# Internal IPs for Debug Toolbar
# ====================================================
INTERNAL_IPS = ["127.0.0.1", "localhost", "0.0.0.0"]

# ====================================================
# Development CORS - Allow all origins
# ====================================================
CORS_ALLOW_ALL_ORIGINS = True

# ====================================================
# Use in-memory cache for development (or Redis if available)
# ====================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "restaurant-portal-dev",
    }
}

# ====================================================
# Celery: Run tasks synchronously in development (optional)
# ====================================================
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True

# ====================================================
# Sentry (disabled in development)
# ====================================================
SENTRY_DSN = env("SENTRY_DSN", default="")