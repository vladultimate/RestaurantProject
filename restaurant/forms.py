from django import forms
from .models import Dish, Category, Order, Feedback

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class GuestCartForm(forms.Form):
    phone = forms.CharField(max_length=20, required=True)
    dish_id = forms.IntegerField()
    quantity = forms.IntegerField(min_value=1, initial=1)

class CheckoutForm(forms.Form):
    address = forms.CharField(
        label="Адреса доставки",
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введіть вашу адресу"
        })
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введіть ваш телефон"
        })
    )


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'price', 'category', 'description', 'image']

class DishEditForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'price', 'category', 'description', 'image']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class CategoryEditForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['description', 'rating'] 
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Напишіть відгук...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5})
        }