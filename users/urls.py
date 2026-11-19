from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentCreateView, PaymentStatusView, UserViewSet, PaymentViewSet, RegisterView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/status/', PaymentStatusView.as_view(), name='payment-status'),
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]
