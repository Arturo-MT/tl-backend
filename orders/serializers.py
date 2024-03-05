from orders.models import Product, Store, Order, OrderItem
from users.models import User
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CurrentUserDefault
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class StoreSerializer(ModelSerializer):
    owner = PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=CurrentUserDefault()
    )
    
    class Meta:
        model = Store
        fields = '__all__'

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['paid', 'customer_email', 'store', 'customer']

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'