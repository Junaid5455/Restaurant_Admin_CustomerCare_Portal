"""
Production-specific settings.

- DEBUG = False
- Security hardened
- HTTPS enforced
- Sentry error tracking
- PostgreSQL Connection Pooling & Timeouts
"""
from .base import *  # noqa: F401, F403
from .base import env

# ====================================================
# Debug Mode — STRICTLY False
# ====================================================
DEBUG = False

# ====================================================
# Allowed Hosts
# ====================================================
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ====================================================
# Database Configuration (Production Grade)
# ====================================================
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": env("DB_NAME", default="restaurant_portal"),
        "USER": env("DB_USER", default="restaurant_user"),
        "PASSWORD": env("DB_PASSWORD", default="secure_password_123"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "ATOMIC_REQUESTS": True,  # Wrap each HTTP request in a transaction
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=600),  # Persistent connections
        "OPTIONS": {
            "connect_timeout": env.int("DB_CONN_TIMEOUT", default=10),
            "options": "-c statement_timeout=30000",  # 30 seconds timeout
            "sslmode": "require",  # Force SSL in production
        },
    }
}

# ====================================================
# Security Configuration
# ====================================================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ====================================================
# CSRF Trusted Origins
# ====================================================
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# ====================================================
# CORS Configuration (strict)
# ====================================================
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# ====================================================
# Static files compression
# ====================================================
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ====================================================
# Email Configuration
# ====================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# ====================================================
# Logging - More conservative in production
# ====================================================
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "INFO"  # noqa: F405

# ====================================================
# Sentry Integration (Optional)
# ====================================================
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment="production",
    )

# ====================================================
# Throttle limits for production
# ====================================================
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "60/hour",
    "user": "1000/hour",
}