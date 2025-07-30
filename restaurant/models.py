from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Dish(models.Model):
    price = models.IntegerField()
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    description = models.TextField()
    

class Feedback(models.model):
    rating = models.IntegerField()
    description = models.CharField(max_length=250)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
