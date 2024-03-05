from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import ProductViewSet, StoreViewSet, OrderViewSet, OrderItemViewSet, ProductStoreViewSet, StoreOrderViewSet, StoreOrderItemViewSet
from users.views import UserCreateView, UserDetailView
from payments.views import CheckoutSessionView, WebhookView

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('stores/<int:store_pk>/products/', ProductStoreViewSet.as_view({
    'get': 'list',  # List products in a store
    'post': 'create',  # Create a product in a store
    'put': 'update',  # Update a product in a store
    'delete': 'destroy',  # Delete a product in a store
}), name='store-products-list'),
    path('stores/<int:store_pk>/products/<int:pk>/', ProductStoreViewSet.as_view({
        'get': 'retrieve',  # Get a product in a store
        'put': 'update',  # Update a product in a store
        'delete': 'destroy',  # Delete a product in a store
        }), name='store-products-detail'),
    path('stores/<int:store_pk>/orders/', StoreOrderViewSet.as_view({
    'get': 'list',  # List orders in a store
    'post': 'create',  # Create an order in a store
    'put': 'update',  # Update an order in a store
    'delete': 'destroy',  # Delete an order in a store
}), name='store-orders-list'),
    path('stores/<int:store_pk>/orders/<int:pk>/', StoreOrderViewSet.as_view({
        'get': 'retrieve',  # Get an order in a store
        'put': 'update',  # Update an order in a store
        'delete': 'destroy',  # Delete an order in a store
        }), name='store-orders-detail'),
    path('stores/<int:store_pk>/orders/<int:order_pk>/order-items/', StoreOrderItemViewSet.as_view({
        'get': 'list',  # List order items in an order
        'post': 'create',  # Create an order item in an order
        'put': 'update',  # Update an order item in an order
        'delete': 'destroy',  # Delete an order item in an order
        }), name='order-order-items-list'),
    path('stores/<int:store_pk>/orders/<int:order_pk>/order-items/<int:pk>/', StoreOrderItemViewSet.as_view({
        'get': 'retrieve',  # Get an order item in an order
        'put': 'update',  # Update an order item in an order
        'delete': 'destroy',  # Delete an order item in an order
        }), name='order-order-items-detail'),
    path('stores/<int:store_pk>/orders/<int:order_id>/checkout/', CheckoutSessionView.as_view(), name='checkout-session'),
    path('webhook/', WebhookView.as_view(), name='webhook'),
]
