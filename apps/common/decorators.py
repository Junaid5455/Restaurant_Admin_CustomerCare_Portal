from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {'detail': 'Authentication required.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if request.user.role not in roles:
                return Response(
                    {'detail': 'You do not have permission to access this resource.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_customer(view_func):
    return require_role('CUSTOMER')(view_func)

def require_restaurant_owner(view_func):
    return require_role('RESTAURANT_OWNER')(view_func)

def require_staff(view_func):
    return require_role('RESTAURANT_STAFF', 'DELIVERY_STAFF')(view_func)

def require_admin(view_func):
    return require_role('SUPER_ADMIN')(view_func)