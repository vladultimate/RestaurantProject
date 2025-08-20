from django.urls import path
from django.conf import settings
from .views import RegisterView, LoginView, HomeView, MenuView, CartView, AddToCartView, CheckoutView, DishCreateView, CategoryCreateView
from django.conf.urls.static import static

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path("add-to-cart/", AddToCartView.as_view(), name="add_to_cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path('create-dish/', DishCreateView.as_view(), name='create_dish'),
    path('create-dish/', CategoryCreateView.as_view(), name='create_category'),

]

urlpatterns += static('/images/', document_root=settings.BASE_DIR / 'images')