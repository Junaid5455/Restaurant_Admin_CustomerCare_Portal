from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = DefaultRouter()
router.register(r'addresses', views.SavedAddressViewSet, basename='addresses')
router.register(r'favorites/restaurants', views.FavoriteRestaurantViewSet, basename='favorite-restaurants')
router.register(r'favorites/items', views.FavoriteMenuItemViewSet, basename='favorite-items')
router.register(r'gift-cards', views.GiftCardViewSet, basename='gift-cards')
router.register(r'campaigns', views.CampaignViewSet, basename='campaigns')
router.register(r'preferences', views.NotificationPreferenceViewSet, basename='preferences')
router.register(r'notifications', views.NotificationViewSet, basename='notifications')

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
    
    # Email verification & Password reset
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('request-verification/', views.RequestEmailVerificationView.as_view(), name='request_verification'),
    path('send-verification/', views.SendVerificationEmailView.as_view(), name='send_verification'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    # Account Management endpoints
    path('rewards/', views.RewardView.as_view(), name='rewards'),
    
    # Include the routers
    path('', include(router.urls)),
]