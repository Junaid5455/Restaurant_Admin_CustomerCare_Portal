"""
Custom exception handlers and exception classes for the
Restaurant Portal API.
"""
import logging

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats all API errors consistently.

    Response format:
    {
        "success": false,
        "message": "Human-readable error message",
        "errors": {  # Detailed error info (if any)
            "field": ["Error details"]
        }
    }
    """
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — log and return 500
        logger.error(
            "Unhandled exception in view %s: %s",
            context.get("view", "unknown"),
            exc,
            exc_info=True,
        )
        return Response(
            {
                "success": False,
                "message": "An internal server error occurred.",
                "errors": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Determine appropriate message based on exception type
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        message = "Authentication credentials were not provided or are invalid."
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, PermissionDenied):
        message = "You do not have permission to perform this action."
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, NotFound):
        message = "The requested resource was not found."
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, MethodNotAllowed):
        message = f"Method {exc.args[0]} is not allowed."
        status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    elif isinstance(exc, ValidationError):
        message = "Validation error occurred."
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        message = str(exc) or "An error occurred."
        status_code = response.status_code

    response.data = {
        "success": False,
        "message": message,
        "errors": response.data if isinstance(response.data, dict) else {"detail": str(response.data)},
    }
    response.status_code = status_code

    # Log errors
    if status_code >= 500:
        logger.error("API Error: %s - %s", status_code, exc, exc_info=True)
    elif status_code >= 400:
        logger.warning("API Error: %s - %s", status_code, exc)

    return response


class AppException(Exception):
    """
    Base custom application exception.

    Usage:
        raise AppException("Custom message", status_code=400)
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "An application error occurred."
    default_code = "application_error"

    def __init__(self, message=None, status_code=None, error_code=None):
        self.message = message or self.default_message
        if status_code:
            self.status_code = status_code
        self.error_code = error_code or self.default_code
        super().__init__(self.message)


class BadRequestException(AppException):
    """Raised for bad request errors (400)."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Bad request."
    default_code = "bad_request"


class NotFoundException(AppException):
    """Raised when a resource is not found (404)."""

    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Resource not found."
    default_code = "not_found"


class ConflictException(AppException):
    """Raised on resource conflicts (409)."""

    status_code = status.HTTP_409_CONFLICT
    default_message = "Resource conflict."
    default_code = "conflict"


class ForbiddenException(AppException):
    """Raised when access is forbidden (403)."""

    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Access forbidden."
    default_code = "forbidden"


class PaymentRequiredException(AppException):
    """Raised when payment is required (402)."""

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_message = "Payment required."
    default_code = "payment_required"


class RateLimitExceededException(AppException):
    """Raised when rate limit is exceeded (429)."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Rate limit exceeded. Please try again later."
    default_code = "rate_limit_exceeded"