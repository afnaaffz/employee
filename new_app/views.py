from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from new_app.forms import Login_Form, Consumer_Register_Form, Industry_Register_Form, Feedback_Form, \
    Product_Form, Complaint_Form, Job_Listing_Form, Meeting_Form, RSVP_Form, Job_Application_Form
from new_app.models import ConsumerRegister, IndustryRegister, Login, Feedback, Product, Order, Complaint, \
    ComplaintResponse, Notification, ApprovedIndustryByAdmin, Payment, JobListing


# Create your views here.

def index(request):
    products = Product.objects.all()
    return render(request, "index.html", {'products': products})

@login_required(login_url = 'login')
def indexx(request):
    return render(request,"indexx.html")


def auth_login(request, user):
    pass

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

def login(request):
    if request.method == "POST":
        username = request.POST.get("uname")
        password = request.POST.get("pass")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user is an industry user and approved
            if user.is_industry and not user.is_approved:
                messages.error(request, "Your account is awaiting approval. Please try again later.")
                return redirect("login")

            # If user is an approved industry user logging in for the first time
            if user.is_industry and user.is_approved and not user.has_logged_in:
                user.has_logged_in = True
                user.save()

            # Log the user in
            auth_login(request, user)

            # Redirect to the original page if specified in the 'next' parameter
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            # Otherwise, redirect based on user type
            if user.is_staff:
                return redirect("admin_view_industry")
            elif user.is_consumer:
                return redirect("consumer_view_industry")
            elif user.is_industry:
                return redirect("industry_profile")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "login.html")

#admin
def adminbase(request):
    return render(request,"admin/admin base.html")

@login_required(login_url = 'login')
def admin_view_consumer(request):
    # Fetch all consumers (approved, rejected, or awaiting approval)
    data = ConsumerRegister.objects.select_related('user').all()
    return render(request, "admin/admin_view_consumers.html", {'data': data})


#industry
@login_required(login_url = 'login')
def industry(request):
    return render(request,"industry/industry.html")

def industrybase(request):
    industry_name = None
    if request.user.is_authenticated and request.user.is_industry:
        # Get the IndustryRegister instance associated with the logged-in user
        industry = IndustryRegister.objects.filter(user=request.user).first()
        if industry:
            industry_name = industry.name
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


@login_required(login_url = 'login')
def view_industry(request):
    # Fetch all industries with their related products
    data = IndustryRegister.objects.prefetch_related('product_set').all()
    return render(request, "industry/view_industry.html", {'data': data})




from django.db.models import Q

def consumer_view_industry(request):
    selected_location = request.GET.get('location', '')
    search_term = request.GET.get('search', '').strip()

    # Get all industries, optionally filtering by location
    industries = IndustryRegister.objects.all()

    if selected_location:
        industries = industries.filter(location=selected_location)

    if search_term:
        industries = industries.filter(
            Q(name__icontains=search_term) |  # Filter by Industry Name
            Q(product__name__icontains=search_term)  # Filter by Product Name
        ).distinct()

    # Get distinct locations for the location dropdown
    locations = IndustryRegister.objects.values_list('location', flat=True).distinct()

    # Check for a message flag in the request
    if 'added' in request.GET:
        messages.success(request, "Product added successfully!")

    return render(request, "consumer/consumer_view_industry.html", {
        'industries': industries,
        'locations': locations,
        'selected_location': selected_location,
    })



@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    industry = product.industry

    # Check if a 'Buy Now' button was pressed
    if request.method == 'POST':
        # Assume quantity 1 for simplicity
        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=1,
            total_price=Decimal(product.price),  # Set total price for the single item
            status="Pending"
        )
        return redirect('payment_page', order_id=order.id)

    return render(request, "consumer/product_detail.html", {
        'product': product,
        'industry': industry,
    })


@login_required(login_url = 'login')
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




@login_required(login_url = 'login')
def update_industry(request,id):
    a = IndustryRegister.objects.get(id=id)
    form = Industry_Register_Form(instance=a)
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST,instance=a)
        if form.is_valid():
            form.save()
            return redirect("admin_view_industry")

    return render(request, "admin/update_products.html", {'form': form})

@login_required(login_url = 'login')
def delete_industry(request, id):
    industry = get_object_or_404(IndustryRegister, id=id)
    industry.delete()
    return redirect('admin_view_industry')



# Admin approves industry user
@login_required(login_url = 'login')
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
@login_required(login_url = 'login')
def reject_industry(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_approved = False
    user.is_rejected = True  # Mark as rejected
    user.save()

    # Remove from ApprovedIndustryByAdmin if previously approved
    ApprovedIndustryByAdmin.objects.filter(industry__user=user).delete()
    return redirect("admin_view_industry")






#consumer
@login_required(login_url = 'login')
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


@login_required(login_url = 'login')
def view_consumer(request):
    data = ConsumerRegister.objects.all()
    print(data)
    return render(request,"consumer/consumer_view_industry.html",{'data':data})



# Admin approves consumer user
@login_required(login_url = 'login')
def approve_consumer(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"Consumer {user.username} has been approved.")
    return redirect('admin_view_consumer')

# Admin rejects consumer user
@login_required(login_url = 'login')
def reject_consumer(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_rejected = True
    user.save()
    messages.success(request, f"Consumer {user.username} has been rejected.")
    return redirect('admin_view_consumer')






@login_required(login_url = 'login')
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
            return redirect("view")  # Redirect to a feedback view page
        else:
            # Form is invalid, errors will be displayed in the template
            return render(request, "consumer/feedback.html", {"form": form})

    return render(request, "consumer/feedback.html", {"form": form})  # Render the form

def view(request):
    # Get the logged-in user's feedback
    data = Feedback.objects.all()

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


@login_required(login_url = 'login')
def reply_feedback(request,id):
    feedback = Feedback.objects.get(id=id)
    if request.method == 'POST':
        r = request.POST.get('reply')
        feedback.reply = r
        feedback.save()
        messages.info(request,' Reply send for complaint')
        return redirect('feedbacks')
    return render(request, 'industry/reply_feedback.html',{'feedback':feedback})


from django.shortcuts import redirect
from django.contrib import messages

def add_product(request):
    if request.method == 'POST':
        # Handle form submission
        form = Product_Form(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.industry = IndustryRegister.objects.get(user=request.user)
            product.save()
            # Add success message to session
            request.session['success_message'] = "Product added successfully!"
            return redirect('product_list')
    else:
        form = Product_Form()

    return render(request, 'industry/add_product.html', {'form': form})

from django.contrib import messages

def product_list(request):
    try:
        industry = IndustryRegister.objects.get(user=request.user)
        products = Product.objects.filter(industry=industry)
    except IndustryRegister.DoesNotExist:
        products = Product.objects.none()

    # Check for success message in session


    return render(request, 'industry/product_list.html', {'products': products})


@login_required(login_url = 'login')
def update_product(request,id):
    a = Product.objects.get(id=id)
    form = Product_Form(instance=a)
    if request.method == 'POST':
        form = Product_Form(request.POST,instance=a)
        if form.is_valid():
            form.save()
            return redirect("product_list")

    return render(request, "industry/update_product.html", {'form': form})



@login_required(login_url = 'login')
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


from django.db.models import Q

def consumer_view_products(request):
    industry_type = request.GET.get('industry_type', None)
    industries = IndustryRegister.objects.values('industry_type').distinct()
    if industry_type:
        products = Product.objects.filter(industry__industry_type=industry_type)
    else:
        products = Product.objects.all()
    return render(request, 'consumer/consumer_view_products.html', {
        'products': products,
        'industries': industries
    })



@login_required
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        total_price = product.price * quantity

        # Create Order
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            total_price=total_price
        )

        return redirect('payment_page', order_id=order.id)

    # Fetch the user's consumer profile and pass to template
    consumer_profile = ConsumerRegister.objects.get(user=user)

    return render(request, 'consumer/consumer_purchase_product.html', {
        'product': product,
        'user': user,
        'consumer_profile': consumer_profile
    })




from decimal import Decimal

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total_amount = order.total_price

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        discount_applied = Decimal(request.POST.get('discount', '0'))

        # Capture optional fields based on the selected payment method
        bank = request.POST.get('bank') if payment_method == 'Net Banking' else None
        emi_duration = request.POST.get('emi_duration') if payment_method == 'EMI' else None
        wallet = request.POST.get('wallet') if payment_method == 'Wallets' else None
        card_number = request.POST.get('card_number') if payment_method == 'Credit/Debit Card' else None
        upi_id = request.POST.get('upi_id') if payment_method == 'UPI' else None

        # Create Payment record
        payment = Payment.objects.create(
            user=request.user,
            order=order,
            payment_method=payment_method,
            total_amount=total_amount - discount_applied,
            discount_applied=discount_applied,
            payment_status="Completed",
            bank=bank,
            emi_duration=emi_duration,
            wallet=wallet,
            card_number=card_number,
            upi_id=upi_id,
        )

        # Redirect to a success page after payment
        return redirect('payment_success', payment_id=payment.id)

    return render(request, 'consumer/consumer_payment_page.html', {
        'order': order,
        'total_amount': total_amount
    })

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'consumer/payment_success.html', {
        'payment': payment
    })



@login_required(login_url = 'login')
def consumer_purchase_confirm(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'consumer/consumer_purchase_confirm.html', {'product': product})


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

def view_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)  # Only get complaints by logged-in user
    return render(request, 'consumer/view_complaints.html', {'complaints': complaints})

@login_required(login_url = 'login')
def view_complaint_detail(request, complaint_id):
    # Fetch the complaint belonging to the logged-in user
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    complaint_response = ComplaintResponse.objects.filter(complaint=complaint).first()

    return render(request, 'consumer/view_complaint_detail.html', {
        'complaint': complaint,
        'complaint_response': complaint_response
    })


def admin_view_complaints(request):
    complaints = Complaint.objects.select_related('user').all()  # Use select_related to fetch user data efficiently
    return render(request, 'admin/admin_view_complaints.html', {'complaints': complaints})

@login_required(login_url = 'login')
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



@login_required(login_url = 'login')
def industry_profile(request):
    a = get_object_or_404(IndustryRegister, user=request.user)  # Get industry associated with logged-in user
    form = Industry_Register_Form(instance=a)
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return redirect("industry_profile")
    return render(request, "industry/industry_profile.html", {'form': form})




def order_history(request):
    # Get the logged-in user's consumer register
    try:
        consumer = ConsumerRegister.objects.get(user=request.user)
        orders = Order.objects.filter(user=request.user)  # Retrieve orders for the logged-in user
    except ConsumerRegister.DoesNotExist:
        consumer = None  # In case the consumer register doesn't exist

    return render(request, 'consumer/order_history.html', {'orders': orders, 'consumer': consumer})


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'consumer/order_detail.html', {'order': order})

def reorder(request, order_id):
    previous_order = Order.objects.get(id=order_id, user=request.user)
    new_order = Order.objects.create(
        user=request.user,
        product=previous_order.product,
        quantity=previous_order.quantity,
        total_price=previous_order.total_price,
        status="Pending"
    )
    return redirect('order_history')


from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.db.models import Avg
from .models import Feedback
import json

def feedback_ratings_graph(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")

    industry_ratings = (Feedback.objects
                        .values('industry__name')
                        .annotate(avg_rating=Avg('rating'))
                        .order_by('-avg_rating'))

    if not industry_ratings:
        print("No data found for industry feedback ratings.")
        return render(request, 'admin/feedback_ratings_graph.html')

    industry_names = [entry['industry__name'] for entry in industry_ratings]
    avg_ratings = [entry['avg_rating'] for entry in industry_ratings]

    context = {
        'industry_names': json.dumps(industry_names),
        'avg_ratings': json.dumps(avg_ratings),
    }

    return render(request, 'admin/feedback_ratings_graph.html', context)

from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.db.models import Count
from .models import Complaint
import json

from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import render
import json

from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import render
import json

from django.db.models import Count
from django.shortcuts import render
import json

def complaints_pie_chart(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch all complaints grouped by product
    complaints_count = (
        Complaint.objects
        .values('product__name')
        .annotate(total_complaints=Count('id'))
        .order_by('-total_complaints')
    )

    # Check if complaints data is available
    if not complaints_count.exists():
        return render(request, 'admin/complaints_pie_chart.html', {'no_data': True})

    # Extract product names and complaint counts
    product_names = [entry['product__name'] for entry in complaints_count]
    complaint_counts = [entry['total_complaints'] for entry in complaints_count]

    context = {
        'product_names': json.dumps(product_names),
        'complaint_counts': json.dumps(complaint_counts),
    }

    return render(request, 'admin/complaints_pie_chart.html', context)


from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.db.models import Sum
from .models import Order
import json

def products_pie_chart(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Query to get total quantities ordered per product
    product_orders = (Order.objects
                      .values('product__name')
                      .annotate(total_ordered=Sum('quantity'))
                      .order_by('-total_ordered'))

    if not product_orders:
        print("No data found for product orders.")
        return render(request, 'admin/products_pie_chart.html')

    # Extract product names and their total quantities ordered
    product_names = [entry['product__name'] for entry in product_orders]
    order_counts = [entry['total_ordered'] for entry in product_orders]

    context = {
        'product_names': json.dumps(product_names),
        'purchase_counts': json.dumps(order_counts),
    }

    return render(request, 'admin/products_pie_chart.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order

# Industry: Update order status
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        return redirect('order_list')  # Redirect to a relevant page
    return render(request, 'industry/update_order_status.html', {'order': order})

# Consumer: Track order status
@login_required
def track_order(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'consumer/track_order.html', {'orders': orders})


@login_required
def order_list(request):
    try:
        # Retrieve the IndustryRegister for the logged-in user
        industry = IndustryRegister.objects.get(user=request.user)
        # Filter orders by the industry of the logged-in user
        orders = Order.objects.filter(product__industry=industry)
    except IndustryRegister.DoesNotExist:
        # If no industry is registered, handle appropriately (e.g., no orders found)
        orders = Order.objects.none()  # No orders if industry doesn't exist

    return render(request, 'industry/order_list.html', {'orders': orders})


from django.shortcuts import render
from .models import Product, Order, ConsumerRegister


def consumer_dashboard(request):
    # Get consumer data
    consumer = ConsumerRegister.objects.get(user=request.user)

    # Example: Fetch recommended products (you can refine this as discussed earlier)
    recommended_products = Product.objects.filter(availability_status='Available')[:5]  # Recommend top 5 products

    # Example: Fetch order history
    order_history = Order.objects.filter(user=request.user)

    context = {
        'consumer': consumer,
        'recommended_products': recommended_products,
        'order_history': order_history,
    }
    return render(request, 'consumer/consumer_dashboard.html', context)







from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import JobApplication





from django.shortcuts import render, redirect

from django.shortcuts import render, redirect




from django.shortcuts import render


from django.shortcuts import render



from django.shortcuts import render, get_object_or_404



from django.shortcuts import render, get_object_or_404, redirect
from .models import Meeting, RSVP
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

# Admin: Add Meeting View
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import IndustryRegister, Meeting


@staff_member_required
def add_meeting(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')

        # Set the industry automatically (replace with appropriate logic)
        try:
            # Assuming you have a specific industry to assign, e.g., industry ID = 1
            industry = IndustryRegister.objects.get(id=1)  # Replace with dynamic logic as needed

            meeting = Meeting.objects.create(
                title=title,
                description=description,
                location=location,
                industry=industry
            )
            return redirect('meeting_list')  # Replace with your meeting list URL name
        except IndustryRegister.DoesNotExist:
            messages.error(request, "Industry does not exist.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('add_meeting')

    return render(request, 'admin/add_meeting.html')


# Admin: View Meetings and Attendance
@staff_member_required
def meeting_list(request):
    meetings = Meeting.objects.all()
    return render(request, 'admin/meeting_list.html', {'meetings': meetings})

@login_required
def view_meeting_list(request):
    meetings = Meeting.objects.all()
    return render(request, 'industry/view_meeting_list.html', {'meetings': meetings})



# Industry: View Meeting and RSVP
from django.contrib import messages

@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        RSVP.objects.update_or_create(
            user=request.user, meeting=meeting, defaults={'status': status}
        )
        messages.success(request, "RSVP updated successfully!")  # Add success message
        return redirect('meeting_detail', pk=meeting.pk)

    user_rsvp = RSVP.objects.filter(user=request.user, meeting=meeting).first()
    return render(request, 'industry/meeting_detail.html', {'meeting': meeting, 'user_rsvp': user_rsvp})


# Admin: Check RSVPs
@staff_member_required
def rsvp_list(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    rsvps = RSVP.objects.filter(meeting=meeting)
    return render(request, 'admin/rsvp_list.html', {'meeting': meeting, 'rsvps': rsvps})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import JobListing, JobApplication

# Create a job post
@login_required
def create_job_post(request):
    if request.method == "POST":
        form = Job_Listing_Form(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.industry = request.user
            job.is_approved = True  # Automatically approve
            job.save()
            return redirect('industry_job_list')
    else:
        form = Job_Listing_Form()
    return render(request, 'industry/create_job.html', {'form': form})

from django.contrib import messages

@login_required
def consumer_job_list(request):
    # Check for approved applications where the user has not been notified
    approved_applications = JobApplication.objects.filter(
        applicant=request.user,
        application_status=JobApplication.APPROVED,
        notified=False
    )

    # Generate a message for each approved application
    for application in approved_applications:
        messages.success(
            request,
            f"Congrats! You have been approved by {application.job.industry.username} for the job '{application.job.title}'."
        )
        # Mark as notified
        application.notified = True
        application.save()

    jobs = JobListing.objects.filter(is_approved=True).order_by('-posted_date')
    return render(request, 'consumer/consumer_job_list.html', {'jobs': jobs})



def industry_job_list(request):
    jobs = JobListing.objects.filter(industry=request.user).order_by('-posted_date')
    return render(request, 'industry/industry_job_list.html', {'jobs': jobs})


# View applications for a specific job
@login_required
def view_job_applications(request, job_id):
    job = get_object_or_404(JobListing, id=job_id, industry=request.user)
    applications = job.get_applications()
    return render(request, 'industry/view_applications.html', {'job': job, 'applications': applications})

# Approve or reject a job application
from django.contrib import messages

@login_required
def manage_application(request, application_id, action):
    application = get_object_or_404(JobApplication, id=application_id, job__industry=request.user)
    if action == 'approve':
        application.approve()
        messages.success(request, f"Application from {application.applicant.username} has been approved!")
    elif action == 'reject':
        application.reject()
        messages.warning(request, f"Application from {application.applicant.username} has been rejected.")
    return redirect('view_job_applications', job_id=application.job.id)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import JobListing, JobApplication

# Consumer Job List

from django.shortcuts import render
from .models import JobListing

@login_required
def consumer_job_list(request):
    jobs = JobListing.objects.filter(is_approved=True).order_by('-posted_date')
    return render(request, 'consumer/consumer_job_list.html', {'jobs': jobs})

# Job Details with Application
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobListing

@login_required  # Ensure the user is logged in
def job_detail_and_apply(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    submitted = False

    if request.method == "POST":
        form = Job_Application_Form(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user  # Assign the logged-in user
            application.save()
            submitted = True
            messages.success(request, "Your application has been submitted successfully.")
        else:
            messages.error(request, "There was an error in your application.")
    else:
        form = Job_Application_Form()

    return render(request, 'consumer/job_detail.html', {
        'job': job,
        'form': form,
        'submitted': submitted,
    })


def logout_view(request):
    logout(request)
    return redirect("login")

