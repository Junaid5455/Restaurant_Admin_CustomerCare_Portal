from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = DefaultRouter()

urlpatterns = [
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Authentication endpoints
    path('register/', views.UserRegistrationViewSet.as_view({'post': 'create'}), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('me/', views.UserProfileView.as_view(), name='current_user'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('request-verification/', views.RequestEmailVerificationView.as_view(), name='request_verification'),
    path('send-verification/', views.SendVerificationEmailView.as_view(), name='send_verification'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    # User endpoints
    # path('', include(router.urls)),
]