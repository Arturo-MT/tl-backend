from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from orders_backend.models import Product, User, Store
from .serializers import ProductSerializer, UserSerializer, StoreSerializer
from .permissions import IsSelfOrStaffOrSuperuser

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrStaffOrSuperuser]

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Store.objects.all()
        return Store.objects.filter(owner=self.request.user)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer