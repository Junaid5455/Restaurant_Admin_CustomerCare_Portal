"""
URLs for the common app — health check endpoints.
"""
from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse(
        {
            "status": "healthy",
            "service": "restaurant_portal",
            "version": "1.0.0",
        }
    )


urlpatterns = [
    path("", health_check, name="health_check"),
]