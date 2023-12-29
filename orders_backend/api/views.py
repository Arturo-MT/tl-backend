from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from orders_backend.models import Product, User, Store, Order, OrderItem
from .serializers import ProductSerializer, UserSerializer, StoreSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsSelfOrStaffOrSuperuser, IsStoreOwnerOrReadOnly, IsProductOwnerOrReadOnly

class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrStaffOrSuperuser]

class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsStoreOwnerOrReadOnly]

    def get_queryset(self):
        return Store.objects.all()
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a store.")
        
        if not self.request.user.is_seller:
            raise PermissionDenied("You must be a seller to create a store.")
        if serializer.validated_data.get('owner') != self.request.user:
            raise PermissionDenied("You can only create a store for yourself.")
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to update a store.")
        
        if serializer.validated_data.get('owner') != self.request.user:
            raise PermissionDenied("You can only update a store that you own.")
        serializer.save(owner=self.request.user)
    
    def perform_destroy(self, instance):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to delete a store.")
        
        if instance.owner != self.request.user:
            raise PermissionDenied("You can only delete a store that you own.")
        instance.delete()

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProductOwnerOrReadOnly]

    def get_queryset(self):
        return Product.objects.all()

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to add products to a store.")
        
        store = serializer.validated_data.get('store')
        if store.owner != self.request.user:
            raise PermissionDenied("You must be the owner of this store to add products to it.")
        serializer.save(store=store)
    
    def perform_update(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to update products in a store.")
        
        store = serializer.validated_data.get('store')
        if store.owner != self.request.user:
            raise PermissionDenied("You must be the owner of this store to update its products.")
        serializer.save(store=store)
    
    def perform_destroy(self, instance):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to delete products from a store.")
        
        if instance.store.owner != self.request.user:
            raise PermissionDenied("You must be the owner of this store to delete its products.")
        instance.delete()
    
class OrderAndOrderItemPagination(PageNumberPagination):
    page_size = 20

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        elif user.is_seller:
            return Order.objects.filter(store__owner=user)
        else:
            return Order.objects.filter(customer=user)
        
class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return OrderItem.objects.all()
        elif user.is_seller:
            return OrderItem.objects.filter(store__owner=user)
        else:
            return OrderItem.objects.filter(order__customer=user)
