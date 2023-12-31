from orders_backend.models import Product, User, Store, Order, OrderItem
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CurrentUserDefault

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name', 'phone_number', 'is_superuser', 'is_seller', 'is_staff', 'owned_stores']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

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

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'