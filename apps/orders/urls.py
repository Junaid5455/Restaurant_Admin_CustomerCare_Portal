"""
URL configuration for the orders app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]