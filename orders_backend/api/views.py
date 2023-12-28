from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from orders_backend.models import Product, User, Store, Order, OrderItem
from .serializers import ProductSerializer, UserSerializer, StoreSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsSelfOrStaffOrSuperuser

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Store.objects.all()
        return Store.objects.filter(owner=user)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Product.objects.all()
        return Product.objects.filter(store__owner=user)
    
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
