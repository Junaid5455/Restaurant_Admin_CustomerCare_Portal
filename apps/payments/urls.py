from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'methods', views.SavedPaymentMethodViewSet, basename='payment-methods')
router.register(r'', views.PaymentViewSet, basename='payments')

urlpatterns = [
    path('', include(router.urls)),
]