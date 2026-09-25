"""
Celery configuration for the Restaurant Portal project.
"""
import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "restaurant_portal.settings.development",
)

app = Celery("restaurant_portal")

# Read configuration from Django settings (prefixed with CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task that prints the request info."""
    print(f"Request: {self.request!r}")