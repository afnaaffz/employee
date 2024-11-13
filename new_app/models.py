from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Login(AbstractUser):
    is_industry = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    has_logged_in = models.BooleanField(default=False)  # New field to track login status

class IndustryRegister(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    location = models.CharField(max_length=100)  # Add location field

    def __str__(self):
        return self.name

class ApprovedIndustryByAdmin(models.Model):
    industry = models.OneToOneField(IndustryRegister, on_delete=models.CASCADE)
    approved_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when approval occurred

    def __str__(self):
        return self.industry.name



class IndustryProfile(models.Model):
    user = models.OneToOneField(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    location = models.CharField(max_length=100)  # Add location field

    def __str__(self):
        return self.name


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
    address = models.TextField()  # Make sure this field exists
    city = models.CharField(max_length=100)  # Add city field if missing
    state = models.CharField(max_length=100)  # Add state field if missing
    zip_code = models.CharField(max_length=10)


    def __str__(self):
        return self.name



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"



class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    industry = models.ForeignKey(IndustryRegister, on_delete=models.CASCADE, related_name="feedbacks")

    subject = models.CharField(max_length=100)
    description = models.TextField()
    rating = models.IntegerField()
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


class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # The user who submits the complaint

    message = models.TextField()
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint {self.id} - {self.message[:30]}"


class ComplaintResponse(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='response')
    response = models.TextField()
    response_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to Complaint {self.complaint.id}"


class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('EMI', 'EMI'),
        ('Net Banking', 'Net Banking'),
        ('Wallets', 'Wallets'),
        ('UPI', 'UPI'),
        ('Credit/Debit Card', 'Credit/Debit Card'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Updated line
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.user.username} - {self.payment_method} - {self.total_amount}"