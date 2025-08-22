from django.contrib import admin
from .models import Dish, Category, Cart, CartItem, Profile, OrderItem, Order

# Register your models here.
admin.site.register(Dish)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(OrderItem)