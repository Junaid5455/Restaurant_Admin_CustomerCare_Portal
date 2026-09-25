"""
Custom permissions for the restaurants app.
"""
from apps.common.permissions import IsRestaurantOwner


class IsRestaurantOwnerOrReadOnly(IsRestaurantOwner):
    """Allows read access to all, write only to restaurant owner."""

    pass