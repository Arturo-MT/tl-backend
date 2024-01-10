from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from orders_backend.models import Product, User, Store, Order, OrderItem
from .serializers import ProductSerializer, UserSerializer, StoreSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsSelfOrStaffOrSuperuser, IsStoreOwnerOrReadOnly, IsProductOwnerOrReadOnly, IsAuthenticatedOrReadOnly

class UserCreateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)

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
    
class ProductStoreViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsProductOwnerOrReadOnly]

    def get_queryset(self):
        store_id = self.kwargs['store_pk']
        return Product.objects.filter(store=store_id)
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to add products to a store.")
        
        store = Store.objects.get(pk=self.kwargs['store_pk'])
        if store.owner != self.request.user:
            raise PermissionDenied("You must be the owner of this store to add products to it.")
        serializer.save(store=store)
    
    def perform_update(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to update products in a store.")
        
        store = Store.objects.get(pk=self.kwargs['store_pk'])
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        elif user.is_seller:
            return Order.objects.filter(store__owner=user)
        else:
            return Order.objects.filter(customer=user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            email = request.data.get('customer_email')
            if not email:
                return Response({'detail': 'You must provide an email to create an order as a non-authenticated user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data['customer'] = request.user.id

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if 'customer' in serializer.validated_data:
            if self.request.user.id != serializer.validated_data['customer'].id:
                raise PermissionDenied("You cannot create orders for other users.")
        serializer.save()

    def perform_update(self, serializer):
        if serializer.validated_data.get('customer') != self.request.user:
            raise PermissionDenied("You can only update your own orders.")
        serializer.save(customer=self.request.user)
    
    def perform_destroy(self):
        return Response({'detail': 'Permission denied: You cannot delete this order.'}, status=status.HTTP_403_FORBIDDEN)
        
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
        
class StoreOrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.kwargs['store_pk']
        if self.request.user.is_seller:
            return Order.objects.filter(store=store_id, store__owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            email = request.data.get('customer_email')
            if not email:
                return Response({'detail': 'You must provide an email to create an order as a non-authenticated user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data['customer'] = request.user.id

        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        store_id = self.kwargs['store_pk']
        if 'customer' in serializer.validated_data:
            if self.request.user.id != serializer.validated_data['customer'].id:
                raise PermissionDenied("You cannot create orders for other users.")
        serializer.save(store=store_id)
    
    def perform_update(self, serializer):
        store_id = self.kwargs['store_pk']
        if serializer.validated_data.get('customer') != self.request.user:
            raise PermissionDenied("You can only update your own orders.")
        serializer.save(store=store_id)

    def destroy(self):
        return Response({'detail': 'Permission denied: You cannot delete this order.'}, status=status.HTTP_403_FORBIDDEN)

class StoreOrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.kwargs['store_pk']
        order_id = self.kwargs['order_pk']
        if self.request.user.is_seller:
            return OrderItem.objects.filter(order=order_id, order__store=store_id, order__store__owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            email = request.data.get('customer_email')
            if not email:
                return Response({'detail': 'You must provide an email to create an order as a non-authenticated user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data['customer'] = request.user.id

        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        store_id = self.kwargs['store_pk']
        order_id = self.kwargs['order_pk']
        if 'customer' in serializer.validated_data:
            if self.request.user.id != serializer.validated_data['customer'].id:
                raise PermissionDenied("You cannot create order items for other users.")
        serializer.save(order=order_id)
    
    def perform_update(self, serializer):
        store_id = self.kwargs['store_pk']
        order_id = self.kwargs['order_pk']
        if serializer.validated_data.get('customer') != self.request.user:
            raise PermissionDenied("You can only update your own order items.")
        serializer.save(order=order_id)

    def destroy(self):
        return Response({'detail': 'Permission denied: You cannot delete this order item.'}, status=status.HTTP_403_FORBIDDEN)
