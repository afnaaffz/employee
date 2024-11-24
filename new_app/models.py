from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, User
from django.db import models


class Login(AbstractUser):
    is_industry = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    has_logged_in = models.BooleanField(default=False)


class IndustryRegister(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    industry_type = models.CharField(max_length=100)  # Type of industry
    mobile = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.industry_type})"





class ApprovedIndustryByAdmin(models.Model):
    industry = models.OneToOneField(IndustryRegister, on_delete=models.CASCADE)
    approved_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when approval occurred

    def __str__(self):
        return self.industry.name





class Product(models.Model):
    industry = models.ForeignKey(IndustryRegister, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.FileField(upload_to='products/')
    availability_status = models.CharField(
        max_length=20, choices=[('Available', 'Available'), ('Out of Stock', 'Out of Stock'), ('Discontinued', 'Discontinued')],
        default='Available'
    )
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Discount field

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    @property
    def discounted_price(self):
        return self.price - (self.price * self.discount_percentage / 100)

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
    zip_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)  # New field for registration timestamp



    def __str__(self):
        return self.name



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50, choices=[('info', 'Information'), ('warning', 'Warning'), ('error', 'Error')], default='info')
    priority = models.IntegerField(default=1)  # Priority for sorting: 1 - Low, 2 - Medium, 3 - High

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)  # Link to Product model
    message = models.TextField()
    complaint_type = models.CharField(max_length=100, choices=[('Product Quality', 'Product Quality'), ('Delivery Issue', 'Delivery Issue'), ('Customer Service', 'Customer Service')], default='Product Quality')  # Complaint type
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Resolved', 'Resolved')], default='Pending')
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_status = models.CharField(max_length=20, default="Pending")
    payment_date = models.DateTimeField(auto_now_add=True)  # Payment date
    bank = models.CharField(max_length=100, blank=True, null=True)
    emi_duration = models.IntegerField(blank=True, null=True)
    wallet = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    upi_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} "

















class Meeting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    industry = models.ForeignKey(IndustryRegister, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class RSVP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    status = models.CharField(choices=[('attending','Attending'),('not_attending', 'Not Attending')],max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}"


class JobListing(models.Model):
    industry = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_listings')  # Assuming Industry is a User
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    posted_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_applications(self):
        return self.applications.all()  # Retrieve all applications for this job

class JobApplication(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    APPLICATION_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')  # Assuming applicant is a consumer User
    application_date = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)
    application_status = models.CharField(
        max_length=10,
        choices=APPLICATION_STATUS_CHOICES,
        default=PENDING,
    )
    notified = models.BooleanField(default=False)  # New field


    def approve(self):
        self.application_status = self.APPROVED
        self.save()

    def reject(self):
        self.application_status = self.REJECTED
        self.save()

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant}"

class VideoTutorial(models.Model):
    industry = models.ForeignKey(IndustryRegister, on_delete=models.CASCADE)  # Link to the industry user
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tutorials')  # Link to the product
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
