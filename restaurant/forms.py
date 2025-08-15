from django import forms

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