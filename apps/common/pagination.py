"""
Custom pagination classes for the Restaurant Portal API.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class providing:
        - Configurable page size (default: 20)
        - page_size query param to override
        - Maximum 100 items per page
        - Standardized response format with metadata
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "Data retrieved successfully",
                "data": data,
                "meta": {
                    "current_page": self.page.number,
                    "next_page_url": self.get_next_link(),
                    "previous_page_url": self.get_previous_link(),
                    "total_pages": self.page.paginator.num_pages,
                    "total_items": self.page.paginator.count,
                    "page_size": self.get_page_size(self.request),
                    "has_next": self.page.has_next(),
                    "has_previous": self.page.has_previous(),
                },
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "message": {"type": "string", "example": "Data retrieved successfully"},
                "data": schema,
                "meta": {
                    "type": "object",
                    "properties": {
                        "current_page": {"type": "integer", "example": 1},
                        "next_page_url": {"type": "string", "nullable": True},
                        "previous_page_url": {"type": "string", "nullable": True},
                        "total_pages": {"type": "integer", "example": 10},
                        "total_items": {"type": "integer", "example": 200},
                        "page_size": {"type": "integer", "example": 20},
                        "has_next": {"type": "boolean", "example": True},
                        "has_previous": {"type": "boolean", "example": False},
                    },
                },
            },
        }


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination class for endpoints that return large datasets (up to 1000)."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class SmallResultsSetPagination(PageNumberPagination):
    """Pagination class for endpoints that return small datasets (10 items)."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50