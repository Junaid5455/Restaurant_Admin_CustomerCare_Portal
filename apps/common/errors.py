from rest_framework import status
from rest_framework.response import Response

def unauthorized_error(message="Authentication credentials were not provided."):
    return Response({"detail": message}, status=status.HTTP_401_UNAUTHORIZED)

def forbidden_error(message="You do not have permission to perform this action."):
    return Response({"detail": message}, status=status.HTTP_403_FORBIDDEN)

def insufficient_role_error(role_name):
    return Response({"detail": f"Only {role_name}s can access this resource."}, status=status.HTTP_403_FORBIDDEN)