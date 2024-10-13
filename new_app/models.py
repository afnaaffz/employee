from django.contrib.auth.models import AbstractUser
from django.db import models


class Login(AbstractUser):
    is_industry = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)  # Add this field




class IndustryRegister(models.Model):
    user = models.OneToOneField(Login,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()
    def __str__(self):
        return self.name





class ConsumerRegister(models.Model):
    user = models.ForeignKey(Login,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return self.name





