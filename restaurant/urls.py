from django.urls import path
from django.conf import settings
from .views import RegisterView, LoginView, HomeView, MenuView
from django.conf.urls.static import static

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu')
]

urlpatterns += static('/images/', document_root=settings.BASE_DIR / 'images')