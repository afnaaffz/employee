from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from new_app.forms import Login_Form, Consumer_Register_Form, Industry_Register_Form, Feedback_Form, \
    Product_Form, Industry_Profile_Form, Complaint_Form
from new_app.models import ConsumerRegister, IndustryRegister, Login, Feedback, Product, Purchase, Order, \
    IndustryProfile, Complaint, ComplaintResponse


# Create your views here.

def index(request):
    products = Product.objects.all()
    return render(request, "index.html", {'products': products})

def indexx(request):
    return render(request,"indexx.html")


from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages


from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render
from django.contrib import messages

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render

def login(request):
    if request.method == "POST":
        username = request.POST.get("uname")
        password = request.POST.get("pass")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user is an industry user and approved
            if user.is_industry and not user.is_approved:
                messages.error(request, "Your account is awaiting approval. Please try again later.")
                return redirect("login")  # Redirect back to login page if not approved

            # If user is an approved industry user logging in for the first time
            if user.is_industry and user.is_approved and not user.has_logged_in:
                user.has_logged_in = True
                user.save()  # Update the user’s `has_logged_in` field

            # Log the user in
            auth_login(request, user)

            # Redirect based on user type
            if user.is_staff:
                return redirect("adminbase")
            elif user.is_consumer:
                return redirect("consumerbase")
            elif user.is_industry:
                return redirect("industrybase")  # Redirect to industry profile view
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "login.html")

#admin
def adminbase(request):
    return render(request,"admin/admin base.html")

def admin_view_consumer(request):
    # Fetch all consumers (approved, rejected, or awaiting approval)
    data = ConsumerRegister.objects.select_related('user').all()
    return render(request, "admin/admin_view_consumers.html", {'data': data})








#industry
def industry(request):
    return render(request,"industry/industry.html")

def industrybase(request):
    return render(request,"industry/industry base.html")


def industry_registration(request):
    form1 = Login_Form()
    form2 = Industry_Register_Form()

    if request.method == "POST":
        form1 = Login_Form(request.POST)
        form2 = Industry_Register_Form(request.POST)

        if form1.is_valid() and form2.is_valid():
            # Save the login form (Login model)
            user = form1.save(commit=False)
            user.is_industry = True
            user.save()

            # Save the industry registration form (IndustryRegister model)
            industry_register = form2.save(commit=False)
            industry_register.user = user
            industry_register.save()

            # Notify user to wait for approval
            messages.info(request, "Registration successful. Please wait for admin approval to log in.")
            return redirect("login")

    return render(request, "industry/industry.html", {'form1': form1, 'form2': form2})


def view_industry(request):
    data = IndustryRegister.objects.all()  # Fetch all industry data
    return render(request, "industry/view_industry.html", {'data': data})  # Pass data to the template



def consumer_view_industry(request):
    selected_name = request.GET.get('name', '')
    data = IndustryRegister.objects.all()

    # Filter by selected name if provided
    if selected_name:
        data = data.filter(name=selected_name)

    # Get distinct names for the dropdown menu
    names = IndustryRegister.objects.values_list('name', flat=True).distinct()

    # Check for a message flag in the request
    if 'added' in request.GET:
        messages.success(request, "Product added successfully!")

    return render(request, "consumer/consumer_view_industry.html", {
        'data': data,
        'names': names,
        'selected_name': selected_name,
    })


from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import Industry_Register_Form
from .models import IndustryRegister


from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .forms import Industry_Register_Form  # Adjust import based on your file structure

def add_industry(request):
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST)

        if form.is_valid():
            try:
                industry = form.save(commit=False)
                industry.user = request.user  # Assign the current logged-in user
                industry.is_approved = False  # Set as pending approval
                industry.is_rejected = False
                industry.save()

                messages.success(request, 'Industry added successfully and is pending approval.')
                return redirect("admin_view_industry")

            except IntegrityError:
                messages.error(request, "An error occurred while trying to add the industry. Please try again.")
        else:
            messages.error(request, "Form is invalid. Please check the details.")
    else:
        form = Industry_Register_Form()

    return render(request, 'admin/add_industry.html', {'form': form})


import logging
logger = logging.getLogger(__name__)

def admin_view_industry(request):
    data = IndustryRegister.objects.all()
    logger.info(f"Number of industries: {data.count()}")
    approved_industries = ApprovedIndustryByAdmin.objects.select_related('industry').all()

    return render(
        request,
        "admin/admin_view_industry.html",
        {
            'data': data,
            'approved_industries': approved_industries
        }
    )




def update_industry(request,id):

    a = IndustryRegister.objects.get(id=id)
    form = Industry_Register_Form(instance=a)
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST,instance=a)
        if form.is_valid():
            form.save()
            return redirect("admin_view_industry")

    return render(request, "admin/update_products.html", {'form': form})

def delete_industry(request, id):
    industry = get_object_or_404(IndustryRegister, id=id)
    industry.delete()
    return redirect('admin_view_industry')


# Admin approves industry user
from django.shortcuts import get_object_or_404, redirect
from .models import Login, IndustryRegister, ApprovedIndustryByAdmin

# Admin approves industry user
def approve_industry(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_approved = True
    user.is_rejected = False  # Optional: Clear any previous rejection status
    user.save()

    # Ensure the industry is registered in ApprovedIndustryByAdmin
    industry = IndustryRegister.objects.get(user=user)
    ApprovedIndustryByAdmin.objects.get_or_create(industry=industry)

    return redirect("admin_view_industry")


# Admin rejects industry user
def reject_industry(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_approved = False
    user.is_rejected = True  # Mark as rejected
    user.save()

    # Remove from ApprovedIndustryByAdmin if previously approved
    ApprovedIndustryByAdmin.objects.filter(industry__user=user).delete()

    return redirect("admin_view_industry")


from django.shortcuts import render
from .models import IndustryRegister, ApprovedIndustryByAdmin




#consumer
def consumer(request):
    return render(request,"consumer/consumer.html")

def consumerbase(request):
    return render(request,"consumer/consumer base.html")

def consumer_registration(request):
    form1 = Login_Form()
    form2 = Consumer_Register_Form()
    if request.method == "POST":
        form1 = Login_Form(request.POST)
        form2 = Consumer_Register_Form(request.POST)

        if form1.is_valid() and form2.is_valid():
            a = form1.save(commit=False)
            a.is_consumer = True
            a.save()
            user1 = form2.save(commit=False)
            user1.user = a
            user1.save()
            return redirect("login")
    return render(request,"consumer/consumer.html", {'form1':form1, 'form2':form2})


def view_consumer(request):
    data = ConsumerRegister.objects.all()
    print(data)
    return render(request,"consumer/consumer_view_industry.html",{'data':data})



# Admin approves consumer user
def approve_consumer(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"Consumer {user.username} has been approved.")
    return redirect('admin_view_consumer')

# Admin rejects consumer user
def reject_consumer(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_rejected = True
    user.save()
    messages.success(request, f"Consumer {user.username} has been rejected.")
    return redirect('admin_view_consumer')






def consumer_notifications(request):
    # Check if the user is authenticated and a consumer
    if request.user.is_authenticated:
        if request.user.is_consumer:
            try:
                consumer_user = ConsumerRegister.objects.get(user=request.user)
                notifications = consumer_user.notifications.all()
                return render(request, 'consumer/consumer_notifications.html', {'notifications': notifications})
            except ConsumerRegister.DoesNotExist:
                return render(request, 'consumer/consumer_notifications.html', {'error': 'No consumer record found.'})
        else:
            return render(request, 'consumer/consumer_notifications.html', {'error': 'User is not a consumer.'})
    else:
        return render(request, 'consumer/consumer_notifications.html', {'error': 'User is not authenticated.'})







def feedback(request):
    form = Feedback_Form()  # Initialize an empty form
    u = request.user  # Get the logged-in user

    if request.method == 'POST':
        form = Feedback_Form(request.POST)  # Capture posted data
        if form.is_valid():  # Validate the form
            obj = form.save(commit=False)  # Create a Feedback instance
            obj.user = u  # Set the user to the logged-in user
            obj.save()  # Save the feedback instance
            return redirect("view")  # Redirect to a view page
        # Form is invalid, errors will be displayed in the template

    return render(request, "consumer/feedback.html", {"form": form})  # Render the form

def view(request):
    # Get the logged-in user's feedback
    data = Feedback.objects.filter(user=request.user)

    # Retrieve the consumer's name associated with the logged-in user
    try:
        consumer = ConsumerRegister.objects.get(user=request.user)
        consumer_name = consumer.name
    except ConsumerRegister.DoesNotExist:
        consumer_name = "Unknown Consumer"

    # Pass the feedback data and consumer's name to the template
    return render(request, "consumer/view.html", {"data": data, "consumer_name": consumer_name})


def feedbacks(request):
    # Get the logged-in user
    user = request.user

    # Try to get the industry registered to the user
    try:
        user_industry = IndustryRegister.objects.get(user=user)
    except IndustryRegister.DoesNotExist:
        user_industry = None  # Handle case where the user does not have an industry

    # Filter feedback based on the user's industry
    feedbacks = Feedback.objects.filter(industry=user_industry) if user_industry else Feedback.objects.none()

    return render(request, 'industry/feedbacks.html', {'feedbacks': feedbacks, 'user_industry': user_industry})


def reply_feedback(request,id):
    feedback = Feedback.objects.get(id=id)
    if request.method == 'POST':
        r = request.POST.get('reply')
        feedback.reply = r
        feedback.save()
        messages.info(request,' Reply send for complaint')
        return redirect('feedbacks')
    return render(request, 'industry/reply_feedback.html',{'feedback':feedback})


def add_product(request):
    if request.method == 'POST':
        form = Product_Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = Product_Form()

    return render(request, 'industry/add_product.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'industry/product_list.html', {'products': products})


def update_product(request,id):

    a = Product.objects.get(id=id)
    form = Product_Form(instance=a)
    if request.method == 'POST':
        form = Product_Form(request.POST,instance=a)
        if form.is_valid():
            form.save()
            return redirect("product_list")

    return render(request, "industry/update_product.html", {'form': form})



def update_products(request, product_id):
    # Fetch the product using the provided ID
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = Product_Form(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()  # Save the updated product data
            messages.success(request, "Product updated successfully.")  # Display success message
            return redirect('consumer_view_products')  # Redirect to the product list page
    else:
        form = Product_Form(instance=product)  # Pre-fill the form with the product's current data

    return render(request, 'consumer/update_products.html', {'form': form, 'product': product})


def consumer_view_products(request):
    products = Product.objects.all()
    return render(request, 'consumer/consumer_view_products.html', {'products': products})


def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        total_price = product.price * quantity

        user = request.user

        # Debugging: Log the user making the purchase
        print(f'Current User: {user.username} (ID: {user.id})')

        # Create the Purchase entry
        purchase = Purchase.objects.create(product=product, user=user, quantity=quantity)

        # Create the Order entry
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            total_price=total_price
        )

        return redirect('consumer/consumer_purchase_confirm', product_id=product.id)

    return render(request, 'consumer/consumer_purchase_product.html', {'product': product})


def consumer_purchase_confirm(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'consumer/consumer_purchase_confirm.html', {'product': product})


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import IndustryRegister





def submit_complaint(request):
    if request.method == 'POST':
        form = Complaint_Form(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)  # Do not save to the database yet
            complaint.user = request.user  # Set the user field with the logged-in user
            complaint.save()  # Now save the complaint with the user information
            messages.success(request, "Complaint submitted successfully.")
            return redirect('view_complaints')
    else:
        form = Complaint_Form()

    return render(request, 'consumer/submit_complaint.html', {'form': form})

@login_required
def view_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)  # Only get complaints by logged-in user
    return render(request, 'consumer/view_complaints.html', {'complaints': complaints})

@login_required
def view_complaint_detail(request, complaint_id):
    # Fetch the complaint belonging to the logged-in user
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    complaint_response = ComplaintResponse.objects.filter(complaint=complaint).first()

    return render(request, 'consumer/view_complaint_detail.html', {
        'complaint': complaint,
        'complaint_response': complaint_response
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Complaint, ComplaintResponse

def admin_view_complaints(request):
    complaints = Complaint.objects.select_related('user').all()  # Use select_related to fetch user data efficiently
    return render(request, 'admin/admin_view_complaints.html', {'complaints': complaints})

def admin_view_complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    # Check if a response already exists for this complaint
    complaint_response = ComplaintResponse.objects.filter(complaint=complaint).first()

    if request.method == 'POST':
        response_text = request.POST.get('response')
        if complaint_response:
            complaint_response.response = response_text
            complaint_response.response_date = timezone.now()
        else:
            complaint_response = ComplaintResponse.objects.create(
                complaint=complaint,
                response=response_text,
                response_date=timezone.now()
            )

        complaint_response.save()
        messages.success(request, "Response submitted successfully.")
        return redirect('admin_view_complaints')

    return render(request, 'admin/admin_view_complaint_detail.html', {
        'complaint': complaint,
        'complaint_response': complaint_response
    })


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

@login_required
def industry_profile(request):
    a = get_object_or_404(IndustryRegister, user=request.user)  # Get industry associated with logged-in user
    form = Industry_Register_Form(instance=a)
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return redirect("industrybase")
    return render(request, "industry/industry_profile.html", {'form': form})
