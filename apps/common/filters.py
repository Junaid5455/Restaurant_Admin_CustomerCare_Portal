"""
Filter utilities for the Restaurant Portal API.
"""
from django_filters import rest_framework as filters


class BaseFilterSet(filters.FilterSet):
    """
    Base filter set providing common filtering options
    for timestamped models.
    """

    created_at__gte = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at__lte = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    updated_at__gte = filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_at__lte = filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )

    class Meta:
        abstract = True


class SoftDeleteFilterSet(BaseFilterSet):
    """Filter set that includes soft-delete filtering."""

    is_deleted = filters.BooleanFilter(field_name="is_deleted")

    class Meta:
        abstract = True


class UUIDFilterSet(filters.FilterSet):
    """Filter helper for UUID-based filtering."""

    uuid = filters.UUIDFilter(field_name="id")

    class Meta:
        abstract = True