from django.contrib import admin
from .models import ProductCategory, Manufacturer, Product, Cart, CartItem

# Register your models here.
admin.site.register(ProductCategory)
admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)