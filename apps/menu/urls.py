from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.MenuCategoryViewSet, basename='menu-category')
router.register(r'items', views.MenuItemViewSet, basename='menu-item')
router.register(r'customizations', views.MenuItemCustomizationViewSet, basename='menu-customization')
router.register(r'addons', views.MenuItemAddOnViewSet, basename='menu-addon')

urlpatterns = [
    path('', include(router.urls)),
]