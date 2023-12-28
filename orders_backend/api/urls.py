from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, UserCreateView, UserDetailView, StoreViewSet, OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
