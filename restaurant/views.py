from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic import CreateView, FormView, TemplateView, View
from django.urls import reverse_lazy, reverse
from .forms import GuestCartForm
from .forms import LoginForm
from .models import Dish, Cart, CartItem


# Create your views here.
class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')  

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Невірний логін або пароль')
            return self.form_invalid(form)


class HomeView(TemplateView):
    template_name = 'home.html'

class MenuView(TemplateView):
    template_name = "menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dishes'] = Dish.objects.all()  
        return context
    
class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.add_for_user(request)
        else:
            return self.add_for_guest(request)

    def add_for_user(self, request):
        dish_id = request.POST.get("dish_id")
        quantity = int(request.POST.get("quantity", 1))

        dish = get_object_or_404(Dish, id=dish_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.create(cart=cart, dish=dish, quantity=quantity)

        return redirect("menu")

    def add_for_guest(self, request):
        form = GuestCartForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            dish_id = form.cleaned_data["dish_id"]
            quantity = form.cleaned_data["quantity"]

            dish = get_object_or_404(Dish, id=dish_id)
            cart, _ = Cart.objects.get_or_create(phone=phone, user=None)
            CartItem.objects.create(cart=cart, dish=dish, quantity=quantity)

        return redirect("menu")
    
class CartView(View):
    def get(self, request):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            phone = request.GET.get("phone")
            cart = Cart.objects.filter(phone=phone, user=None).first()

        cart_items = CartItem.objects.filter(cart=cart) if cart else []

        total_price = sum(item.dish.price * item.quantity for item in cart_items)

        return render(request, "cart.html", {
            "cart_items": cart_items,
            "total_price": total_price
        })