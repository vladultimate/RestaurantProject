from django.urls import path
from django.conf import settings
from .views import RegisterView, LoginView, HomeView, MenuView, CartView, AddToCartView, CheckoutView, DishCreateView, CategoryCreateView, AdminOrdersView, DishEditView, DishDeleteView, CategoryDeleteView, ConfirmOrderView, AddFeedbackView, DeleteFeedbackView, FeedbackListView
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("add-to-cart/", AddToCartView.as_view(), name="add_to_cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path('create-dish/', DishCreateView.as_view(), name='create_dish'),
    path('create-category/', CategoryCreateView.as_view(), name='create_category'),
    path('admin-orders/', AdminOrdersView.as_view(), name='admin_orders'),
    path('<int:pk>/edit/', DishEditView.as_view(), name='edit_dish'),
    path('<int:pk>/delete/', DishDeleteView.as_view(), name='delete_dish'),
    path('confirm-order/', ConfirmOrderView.as_view(), name='confirm_order'),
    path("feedback/add/<int:dish_id>/", AddFeedbackView.as_view(), name="add_feedback"),
    path("feedback/delete/<int:feedback_id>/", DeleteFeedbackView.as_view(), name="delete_feedback"),
    path('feedback/<int:pk>/', FeedbackListView.as_view(), name='feedback_list')
]

urlpatterns += static('/images/', document_root=settings.BASE_DIR / 'images')