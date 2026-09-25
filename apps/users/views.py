from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from apps.users.serializers import (
    CustomUserSerializer, 
    CustomUserCreateSerializer, 
    LoginSerializer, 
    ChangePasswordSerializer
)
from apps.common.responses import SuccessResponse, ErrorResponse
from django.contrib.auth import get_user_model

from apps.users.serializers import EmailVerificationSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from apps.users.models import EmailVerificationToken, PasswordResetToken
from apps.users.email_service import EmailService
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny






User = get_user_model()

class UserRegistrationViewSet(viewsets.ViewSet):
    """ViewSet for user registration"""
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = CustomUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = CustomUserSerializer(user).data
            return SuccessResponse(
                message="Registration successful",
                data={
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": user_data
                },
                status_code=status.HTTP_201_CREATED
            )
        return ErrorResponse(
            message="Registration failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class UserLoginView(APIView):
    """View for user login"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            user_data = CustomUserSerializer(user).data
            return SuccessResponse(
                message="Login successful",
                data={
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": user_data
                }
            )
        return ErrorResponse(
            message="Invalid credentials",
            errors=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class UserLogoutView(APIView):
    """View for user logout"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return ErrorResponse(message="Refresh token is required", status_code=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return SuccessResponse(message="Logout successful")
        except TokenError:
            return ErrorResponse(message="Invalid token", status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ErrorResponse(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """View for retrieving and updating user profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return SuccessResponse(message="Profile retrieved", data=serializer.data)

    def put(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse(message="Profile updated", data=serializer.data)
        return ErrorResponse(message="Update failed", errors=serializer.errors)

class ChangePasswordView(APIView):
    """View for changing user password"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return ErrorResponse(message="Invalid old password", errors={"old_password": ["Incorrect password."]})
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return SuccessResponse(message="Password changed successfully")
        
        return ErrorResponse(message="Password change failed", errors=serializer.errors)





class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            token_obj = EmailVerificationToken.objects.get(token=serializer.validated_data['token'])
            token_obj.is_used = True
            token_obj.used_at = timezone.now()
            token_obj.save()
            
            user = token_obj.user
            user.email_verified = True
            user.email_verified_at = timezone.now()
            user.save()
            
            return SuccessResponse(message="Email verified successfully")
        return ErrorResponse(message="Verification failed", errors=serializer.errors)

class RequestEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        if user.email_verified:
            return SuccessResponse(message="Email already verified")
        
        token = EmailVerificationToken.create_for_user(user)
        email_sent = EmailService.send_verification_email(user, token)
        
        if email_sent:
            return SuccessResponse(message="Verification email sent")
        return ErrorResponse(message="Failed to send email", status_code=500)

class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return ErrorResponse(message="Email required")
        
        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                return SuccessResponse(message="Email already verified")
            
            token = EmailVerificationToken.create_for_user(user)
            email_sent = EmailService.send_verification_email(user, token)
            
            if email_sent:
                return SuccessResponse(message="Verification email sent")
            return ErrorResponse(message="Failed to send email", status_code=500)
        except User.DoesNotExist:
            return ErrorResponse(message="User not found", status_code=404)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            token = PasswordResetToken.create_for_user(user)
            email_sent = EmailService.send_password_reset_email(user, token)
            
            if email_sent:
                return SuccessResponse(message="Password reset email sent")
            return ErrorResponse(message="Failed to send email", status_code=500)
        return ErrorResponse(message="Request failed", errors=serializer.errors)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token_obj = PasswordResetToken.objects.get(token=serializer.validated_data['token'])
            user = token_obj.user
            
            user.set_password(serializer.validated_data['new_password'])
            user.last_password_changed = timezone.now()
            user.save()
            
            token_obj.is_used = True
            token_obj.used_at = timezone.now()
            token_obj.save()
            
            EmailService.send_password_changed_email(user)
            
            return SuccessResponse(message="Password reset successfully")
        return ErrorResponse(message="Reset failed", errors=serializer.errors)