from django.contrib import admin

# Register your models here.

from .models import User, Order, Product, OrderItem

admin.site.register(User)
admin.site.register(Order)
admin.site.register(Product)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    list_filter = ('order', 'product')
    search_fields = ('order__customer__name', 'product__name')
    list_per_page = 20
