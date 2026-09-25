"""
Custom permissions for the orders app.
"""
from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """Allows access only to the order owner."""

    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user