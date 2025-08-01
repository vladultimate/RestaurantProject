from django.db import models
from django.contrib.auth.models import User


class Dish(models.Model):
    price = models.IntegerField()
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    description = models.TextField()
    

class Feedback(models.Model):
    rating = models.IntegerField()
    description = models.CharField(max_length=250)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dishes = models.ManyToManyField(Dish) 