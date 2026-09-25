"""Restaurant Portal main project package."""
from .celery import app as celery_app  # noqa: F401

__all__ = ("celery_app",)
__version__ = "1.0.0"