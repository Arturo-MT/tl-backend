from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, UserCreateView, UserDetailView, StoreViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'stores', StoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
