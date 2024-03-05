from django.contrib import admin

# Register your models here.

from orders.models import Order, Product, OrderItem, Payment, Store
from users.models import User

admin.site.register(User)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Store)
