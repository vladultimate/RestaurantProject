from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView, TemplateView, View, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .forms import GuestCartForm, LoginForm, CheckoutForm, DishForm, CategoryForm, DishEditForm
from .models import Dish, Cart, CartItem, Category, Order, OrderItem


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
    
class CheckoutView(View):
    template_name = "checkout.html"

    def get(self, request):
        form = CheckoutForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["address"]
            phone = form.cleaned_data["phone"]

            # створюємо замовлення
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                address=address,
                phone=phone
            )

            # --- Зареєстрований користувач ---
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(cart__user=request.user)
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        dish=item.dish,
                        quantity=item.quantity
                    )
                # очищаємо корзину
                cart_items.delete()
                Cart.objects.filter(user=request.user).delete()  # опціонально видалити сам Cart

            # --- Гість через сесію ---
            else:
                session_cart = request.session.get("cart", [])
                for item in session_cart:
                    dish = Dish.objects.get(id=item["dish_id"])
                    quantity = item["quantity"]
                    OrderItem.objects.create(
                        order=order,
                        dish=dish,
                        quantity=quantity
                    )
                request.session["cart"] = []

            # рахуємо загальну суму
            order.total_price = sum(
                oi.dish.price * oi.quantity for oi in order.items.all()
            )
            order.save()

            return redirect("home")  # сторінка "Дякуємо за замовлення"

        return render(request, self.template_name, {"form": form})
    
class DishCreateView(LoginRequiredMixin, CreateView):
    model = Dish
    form_class = DishForm
    template_name = 'create_dish.html'
    success_url = '/menu/' 

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != 'admin':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'create_category.html'
    success_url = '/menu/' 

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != 'admin':
            return redirect('menu')
        return super().dispatch(request, *args, **kwargs)
    
class AdminOrdersView(View):
    template_name = "admin_orders.html"

    def get(self, request):
        orders = Order.objects.prefetch_related('items__dish').all()
        orders_data = []

        for order in orders:
            items_list = []
            for item in order.items.all():
                items_list.append({
                    "dish": item.dish,
                    "quantity": item.quantity,
                    "total": item.dish.price * item.quantity
                })
            orders_data.append({
                "order": order,
                "items": items_list,
                "order_total": sum(i["total"] for i in items_list)
            })

        return render(request, self.template_name, {"orders_data": orders_data})

    def post(self, request):
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        order.status = "confirmed"
        order.save()
        return redirect("admin_orders")
    
class DishEditView(UpdateView):
    model = Dish
    form_class = DishEditForm
    template_name = 'create_dish.html'
    success_url = reverse_lazy('menu')

class DishDeleteView(DeleteView):
    model = Dish
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('menu')