from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, User
from django.db import models


class Login(AbstractUser):
    is_industry = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

class IndustryRegister(models.Model):
    user = models.OneToOneField(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    location = models.CharField(max_length=100)  # Add location field

    def __str__(self):
        return self.name


class IndustryProfile(models.Model):
    user = models.OneToOneField(IndustryRegister,on_delete=models.CASCADE)
    profile_pic = models.FileField(upload_to='profilepic/')
    cover_image = models.FileField(upload_to='industry_covers/')

class Product(models.Model):
    industry = models.ForeignKey(IndustryRegister,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10 ,decimal_places=2)
    image = models.FileField(upload_to='products/')

    def __str__(self):
        return self.name






class ConsumerRegister(models.Model):
    user = models.ForeignKey(Login,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    industries = models.ManyToManyField(IndustryRegister, related_name='notifications', blank=True)

    def __str__(self):
        return self.title


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    filter_horizontal = ('industries',)


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    description = models.TextField()
    rating = models.IntegerField()
    reply = models.TextField(null=True, blank=True)  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Updated this line
    purchase_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.user.username} purchased {self.product.name} on {self.purchase_date}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Pending")  # e.g., Pending, Shipped, Delivered

    def __str__(self):
        return f"Order by {self.user.username} for {self.product.name} on {self.order_date}"

    @property
    def calculate_total_price(self):
        return self.product.price * self.quantity