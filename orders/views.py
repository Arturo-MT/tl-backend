from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from orders.models import Product, Store, Order, OrderItem
from orders.serializers import ProductSerializer, StoreSerializer, OrderSerializer, OrderItemSerializer
from users.permissions import IsStoreOwnerOrReadOnly, IsProductOwnerOrReadOnly, IsOrderOwnerOrStoreOwner, IsOrderItemOwnerOrStoreOwner

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

        raise PermissionDenied("You cannot delete a store.")

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

        raise PermissionDenied("You cannot delete products from a store.")
    
class ProductStoreViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsProductOwnerOrReadOnly]

    def get_queryset(self):
        return Product.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(store=self.kwargs['store_pk'])
    
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
        
        raise PermissionDenied("You cannot delete products from a store.")
    
class OrderAndOrderItemPagination(PageNumberPagination):
    page_size = 20

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOrderOwnerOrStoreOwner]

    def get_queryset(self):
        return Order.objects.all()

    def filter_queryset(self, queryset):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.filter(customer_email=self.request.data.get('customer_email'))
        elif user.is_superuser:
            return queryset
        elif user.is_seller:
            return queryset.filter(store__owner=user)
        else:
            return queryset.filter(customer=user)
        

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            email = request.data.get('customer_email')
            if not email:
                return Response({'detail': 'You must provide an email to create an order as a non-authenticated user.'}, status=status.HTTP_400_BAD_REQUEST)
            request.data['customer_email'] = email
        else:
            request.data['customer'] = request.user.id

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if 'customer' in serializer.validated_data:
            if self.request.user.id != serializer.validated_data['customer'].id:
                raise PermissionDenied("You cannot create orders for other users.")
        serializer.save()

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            email = request.data.get('customer_email')
            if not email:
                return Response({'detail': 'You must provide an email to update an order as a non-authenticated user.'}, status=status.HTTP_400_BAD_REQUEST)
            request.data['customer_email'] = email
        else:
            request.data['customer'] = request.user.id

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        if 'customer' in serializer.validated_data:
            if self.request.user.id != serializer.validated_data['customer'].id:
                raise PermissionDenied("You cannot update orders for other users.")
    
    def perform_destroy(self, instance):
        raise PermissionDenied("Orders cannot be deleted.")

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsOrderItemOwnerOrStoreOwner]

    def get_queryset(self):
        return OrderItem.objects.all()

    def filter_queryset(self, queryset):
        user = self.request.user
        if user.is_superuser:
            return queryset
        elif user.is_seller:
            return queryset.filter(order__store__owner=user)
        else:
            return queryset.filter(order__customer=user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            order_id = request.data.get('order')
            if order_id is not None:
                try:
                    order = Order.objects.get(pk=order_id)
                    if order.customer_email is None:
                        return Response({'detail': 'You must provide an email to create an order item for this order.'}, status=status.HTTP_400_BAD_REQUEST)
                except Order.DoesNotExist:
                    return Response({'detail': 'The specified order does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'You must provide an order ID to create an order item as a non-authenticated user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data['customer'] = request.user.id

        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        if 'customer' in serializer.validated_data:
            if self.request.user.id != serializer.validated_data['customer'].id:
                raise PermissionDenied("You cannot create order items for other users.")
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()

        
class StoreOrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.all()

    def filter_queryset(self, queryset):
        store_id = self.kwargs['store_pk']
        if self.request.user.is_seller:
            return queryset.filter(store=store_id, store__owner=self.request.user)
        return queryset
    
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
        return OrderItem.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        store_id = self.kwargs['store_pk']
        order_id = self.kwargs['order_pk']
        if self.request.user.is_seller:
            return queryset.filter(order=order_id, order__store=store_id, order__store__owner=self.request.user)
        return queryset
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            email = request.data.get('customer_email')
            if not email:
                return Response({'detail': 'You must provide an email to create an order as a non-authenticated user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data['customer'] = request.user.id

        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        order_id = self.kwargs['order_pk']
        if 'customer' in serializer.validated_data:
            if self.request.user.id != serializer.validated_data['customer'].id:
                raise PermissionDenied("You cannot create order items for other users.")
        serializer.save(order=order_id)
    
    def perform_update(self, serializer):
        order_id = self.kwargs['order_pk']
        if serializer.validated_data.get('customer') != self.request.user:
            raise PermissionDenied("You can only update your own order items.")
        serializer.save(order=order_id)

    def destroy(self):
        return Response({'detail': 'Permission denied: You cannot delete this order item.'}, status=status.HTTP_403_FORBIDDEN)
