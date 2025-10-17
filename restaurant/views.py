from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView, TemplateView, View, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy, reverse
from .forms import GuestCartForm, LoginForm, CheckoutForm, DishForm, CategoryForm, DishEditForm, CategoryEditForm
from .models import Dish, Cart, CartItem, Category, Order, OrderItem, Feedback


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_dishes'] = Dish.objects.all().order_by('-id')[:3]
        return context
    
class MenuView(TemplateView):
    template_name = "menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dishes = Dish.objects.all()

        for dish in dishes:
            feedbacks = dish.feedbacks.all()
            count = feedbacks.count()
            if count > 0:
                total = sum(fb.rating for fb in feedbacks)
                dish.avg_rating = round(total / count, 1)
            else:
                dish.avg_rating = None

        context['dishes'] = dishes
        return context

SESSION_CART_KEY = "cart"     

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
        item, created = CartItem.objects.get_or_create(cart=cart, dish=dish, defaults={"quantity": quantity})
        if not created:
            item.quantity += quantity
            item.save()
        return redirect("menu")

    def add_for_guest(self, request):
        dish_id = str(request.POST.get("dish_id"))
        quantity = int(request.POST.get("quantity", 1))
        if not dish_id:
            return redirect("menu")
        session_cart = request.session.get(SESSION_CART_KEY, {})
        session_cart[dish_id] = session_cart.get(dish_id, 0) + quantity
        request.session[SESSION_CART_KEY] = session_cart
        request.session.modified = True
        return redirect("menu")


class CartView(View):
    def get(self, request):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            cart_items = CartItem.objects.filter(cart=cart) if cart else []
        else:
            cart_items = self._get_session_cart_items(request)

        total_price = sum(item.dish.price * item.quantity for item in cart_items)
        discount_price = None
        if request.user.is_authenticated:
            discount_price = total_price * 0.90

        return render(request, "cart.html", {
            "cart_items": cart_items,
            "total_price": total_price,
            "discount_price": discount_price
        })

    def _get_session_cart_items(self, request):
        session_cart = request.session.get(SESSION_CART_KEY, {})
        items = []
        for dish_id_str, qty in session_cart.items():
            try:
                dish = Dish.objects.get(id=int(dish_id_str))
            except Dish.DoesNotExist:
                continue
            class TempItem:
                pass
            it = TempItem()
            it.dish = dish
            it.quantity = qty
            items.append(it)
        return items
    
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

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                address=address,
                phone=phone
            )

            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(cart__user=request.user)
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        dish=item.dish,
                        quantity=item.quantity
                    )
                cart_items.delete()
                Cart.objects.filter(user=request.user).delete()

            else:
                session_cart = request.session.get("cart", {})
                for dish_id_str, quantity in session_cart.items():
                    dish = Dish.objects.get(id=int(dish_id_str))
                    OrderItem.objects.create(
                        order=order,
                        dish=dish,
                        quantity=quantity
                    )
                request.session["cart"] = {}
                request.session.modified = True

            order.total_price = sum(
                oi.dish.price * oi.quantity for oi in order.items.all()
            )
            order.save()

            return redirect("home")

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
        orders = Order.objects.prefetch_related('items__dish').order_by('-created_at').all()

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
                "order_total": order.calculate_total()  
            })

        paginator = Paginator(orders_data, 3)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {"page_obj": page_obj})
    
    def post(self, request):
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        order.status = "confirmed"
        order.save()
        return redirect("admin_orders")
    
class DishEditView(UpdateView):
    model = Dish
    form_class = DishEditForm
    template_name = 'edit_dish.html'
    success_url = reverse_lazy('menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dish'] = self.object 
        return context

class DishDeleteView(DeleteView):
    model = Dish
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('menu')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('menu')

class ConfirmOrderView(View):
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        order.confirmed = True
        order.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
class AddFeedbackView(LoginRequiredMixin, View):
    def post(self, request, dish_id):
        dish = get_object_or_404(Dish, id=dish_id)
        rating = request.POST.get("rating")
        description = request.POST.get("description")

        if rating and description:
            feedback = Feedback.objects.create(
                rating=rating,
                description=description,
                author=request.user
            )
            feedback.dishes.add(dish)

        return redirect('feedback_list', pk=dish.id)

class DeleteFeedbackView(LoginRequiredMixin, View):
    def post(self, request, feedback_id):
        feedback = get_object_or_404(Feedback, id=feedback_id)

        if request.user == feedback.author or request.user.profile.role == "admin":
            feedback.delete()

        return redirect("menu")
    

class FeedbackListView(DetailView):
    model = Dish
    template_name = "feedback_list.html"
    context_object_name = "dish"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedbacks'] = self.object.feedbacks.all()
        return context