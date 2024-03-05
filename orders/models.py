from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from users.models import User


# The `Store` class represents a store with attributes such as name, address, phone number, email, and
# a many-to-many relationship with products.
class Store(models.Model):
    name = models.CharField(max_length=50, blank=False)
    address = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    email = models.CharField(max_length=50, blank=False)
    logo = models.ImageField(upload_to='logos', blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='stores')

    products_in_store = models.ManyToManyField('Product', related_name='stores', blank=True)

    def __str__(self):
        return self.name or ''

# The `Product` class represents a product with attributes such as name, description, price, preview
# image, availability, and a foreign key to the `Store` model.
class Product(models.Model):
    name = models.CharField(max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, blank=False)
    preview = models.ImageField(upload_to='products', blank=True, null=True)
    available = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=False, related_name='products')

    def clean(self):
        if self.price < 0:
            raise ValidationError("El precio no puede ser negativo")
        
    def __str__(self):
        return self.name or ''

# The `Order` class represents an order made by a customer in a store, with various status options and
# timestamps.
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='orders')
    customer_email = models.EmailField(blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    paid = models.BooleanField(default=False, editable=False)
    
    STATUS_CHOICES = [
        ('R', 'Received'),
        ('A', 'Accepted'),
        ('D', 'Declined'),
        ('P', 'Paid'),
        ('O', 'On process'),
        ('C', 'Completed'),
        ('X', 'Cancelled'),
    ]

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='R',
        blank=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id}"

# The `OrderItem` class represents an item in an order, with properties such as the order it belongs
# to, the product being ordered, the quantity, a description, and the store it is being ordered from.
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False)
    quantity = models.PositiveIntegerField(default=1, blank=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
# The Payment class represents a payment made for an order, including the amount, payment date, and
# store information.
class Payment(models.Model):
    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE, blank=False)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, blank=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.id}"
