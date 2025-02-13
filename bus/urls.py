from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, BookingViewSet, RouteViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/routes/', RouteViewSet.as_view({'get': 'list'}), name='routes'),

    path('api/', include(router.urls)),
]