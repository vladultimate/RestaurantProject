from django.urls import path
from .views import RegisterView, LoginView, HomeView, MenuView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu')
]