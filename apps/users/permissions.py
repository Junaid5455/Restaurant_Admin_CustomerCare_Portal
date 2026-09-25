from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """Check if user is the object owner"""
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsCustomer(BasePermission):
    """Check if user role is CUSTOMER"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'CUSTOMER'
        )

class IsRestaurantOwner(BasePermission):
    """Check if user role is RESTAURANT_OWNER"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'RESTAURANT_OWNER'
        )

class IsStaffMember(BasePermission):
    """Check if user role is RESTAURANT_STAFF or DELIVERY_STAFF"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['RESTAURANT_STAFF', 'DELIVERY_STAFF']
        )