from django.db import models

class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    password = models.CharField(max_length=50)

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('R', 'Received'),
        ('A', 'Accepted'),
        ('D', 'Declined'),
        ('P', 'Preparing'),
        ('C', 'Completed'),
    ]

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='R',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Pedido {self.id} - {self.customer.username}'

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    preview = models.ImageField(upload_to='products', null=True, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Item {self.quantity} - {self.product.name}'