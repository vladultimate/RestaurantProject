from django.contrib import admin
from .models import Dish, Category, Cart, CartItem, Profile

# Register your models here.
admin.site.register(Dish)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Profile)