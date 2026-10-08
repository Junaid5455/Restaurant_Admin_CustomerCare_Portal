from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'holidays', views.RestaurantHolidayViewSet, basename='holidays')
router.register(r'delivery-zones', views.RestaurantDeliveryZoneViewSet, basename='delivery-zones')
router.register(r'staff', views.StaffMemberViewSet, basename='staff')
router.register(r'', views.RestaurantViewSet, basename='restaurant')

urlpatterns = [
    path('settings/', views.RestaurantSettingsView.as_view(), name='restaurant-settings'),
    path('search/', views.RestaurantViewSet.as_view({'get': 'search'}), name='restaurant_search'),
    path('', include(router.urls)),
]