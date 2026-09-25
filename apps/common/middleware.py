"""
Custom middleware for the Restaurant Portal.
"""
import json
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PermissionLoggingMiddleware(MiddlewareMixin):
    """Log all authorization checks and denials"""
    
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(
                f"Access attempt: {request.user.email} ({request.user.role}) - "
                f"{request.method} {request.path}"
            )
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'user') and request.user.is_authenticated and response.status_code >= 400:
            if response.status_code in [401, 403]:
                logger.warning(
                    f"Access denied: {request.user.email} ({request.user.role}) - "
                    f"{request.method} {request.path} - {response.status_code}"
                )
        return response

# Keep your existing CustomMiddleware and RequestIDMiddleware below if you have them




class CustomMiddleware:
    """
    Custom middleware for:
        - Request/response timing
        - Request logging
        - Adding response headers
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pre-processing: log incoming request
        self.process_request(request)

        response = self.get_response(request)

        # Post-processing: log response
        self.process_response(request, response)

        return response

    def process_request(self, request):
        """Process the request before it reaches the view."""
        request.start_time = time.time()

        # Log API requests (skip static/admin in production)
        if request.path.startswith("/api/"):
            body = ""
            if hasattr(request, "body") and request.body:
                try:
                    body = request.body.decode("utf-8")[:500]
                except (UnicodeDecodeError, AttributeError):
                    body = "[binary data]"

            logger.info(
                "REQUEST: %s %s | Body: %s",
                request.method,
                request.path,
                body,
            )

    def process_response(self, request, response):
        """Process the response before it's sent to the client."""
        duration = time.time() - getattr(request, "start_time", time.time())
        response["X-Response-Time"] = f"{duration:.4f}s"
        response["X-App-Version"] = "1.0.0"

        if request.path.startswith("/api/"):
            if response.status_code >= 400:
                logger.warning(
                    "RESPONSE: %s %s -> %d (%.4fs)",
                    request.method,
                    request.path,
                    response.status_code,
                    duration,
                )
            else:
                logger.info(
                    "RESPONSE: %s %s -> %d (%.4fs)",
                    request.method,
                    request.path,
                    response.status_code,
                    duration,
                )

        return response

    def process_exception(self, request, exception):
        """Handle unhandled exceptions."""
        logger.error(
            "EXCEPTION in %s %s: %s",
            request.method,
            request.path,
            exception,
            exc_info=True,
        )
        return None


class RequestIDMiddleware:
    """
    Middleware that adds a unique request ID to each request.

    The request ID is added to the response headers as
    `X-Request-ID` for traceability.
    """

    HEADER = "X-Request-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import uuid

        request_id = request.headers.get(self.HEADER) or str(uuid.uuid4())
        request.request_id = request_id

        response = self.get_response(request)
        response[self.HEADER] = request_id

        return response