from django.contrib import admin

# Register your models here.

from .models import User, Order, Product, OrderItem, Payment, Store

admin.site.register(User)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Store)
