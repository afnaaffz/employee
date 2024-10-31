from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
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


def auth_login(request, user):
    pass


def login(request):
    if request.method == "POST":
        username = request.POST.get("uname")
        password = request.POST.get("pass")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_industry and user.is_approved and not user.has_logged_in:
                user.has_logged_in = True
                user.save()  # Update the user’s `has_logged_in` field

            auth_login(request, user)

            if user.is_staff:
                return redirect("adminbase")
            elif user.is_consumer:
                return redirect("consumerbase")
            elif user.is_industry:
                return redirect("industrybase")
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



def admin_view_industry(request):
    data = IndustryRegister.objects.select_related('user').all()
    return render(request, "admin/admin_view_industry.html", {'data': data})





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
    # Ensure that the user is an approved industry user
    if request.user.is_industry and request.user.is_approved:
        try:
            # Filter the data to show only the current logged-in user's industry details
            data = IndustryRegister.objects.filter(user=request.user)
            return render(request, "industry/view_industry.html", {'data': data})
        except IndustryRegister.DoesNotExist:
            # If no IndustryRegister entry is found, you can handle it here (e.g., show a message)
            return render(request, "industry/view_industry.html", {'error': 'No industry record found.'})
    else:
        # Redirect or show a message if the user is not authorized or approved
        return render(request, "industry/view_industry.html", {'error': 'You are not authorized to view this page.'})


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


def add_industry(request):
    form = Industry_Register_Form()
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST)
        if form.is_valid():
            industry = form.save(commit=False)  # Don't save to DB yet
            industry.user = request.user         # Assign the current logged-in user
            industry.save()                      # Now save to DB
            return redirect("admin_view_industry")
    return render(request, 'admin/add_industry.html', {'form': form})


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
def approve_industry(request, user_id):
    # Fetch the user and verify they are an industry user
    user = get_object_or_404(Login, pk=user_id, is_industry=True)
    if not user.is_approved:
        user.is_approved = True
        user.is_rejected = False
        user.save()

        # Send email notification
        send_mail(
            'Account Approved',
            f'Hello {user.username}, your account has been approved. You can now log in.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )

        messages.success(request, f'{user.username} has been approved.')
    return redirect('admin_view_industry')

def reject_industry(request, user_id):
    # Fetch the user and verify they are an industry user
    user = get_object_or_404(Login, pk=user_id, is_industry=True)
    if not user.is_rejected:
        user.is_rejected = True
        user.is_approved = False
        user.save()
        messages.success(request, f'{user.username} has been rejected.')
    return redirect('admin_view_industry')

def admin_view_industry(request):
    data = IndustryRegister.objects.filter(user__is_approved=False)
    return render(request, "admin/admin_view_industry.html", {'data': data})

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





def industry_notifications(request):
    if request.user.is_authenticated:
        if request.user.is_industry:
            try:
                industry_user = IndustryRegister.objects.get(user=request.user)
                notifications = industry_user.notifications.all()
                return render(request, 'industry/industry_notifications.html', {'notifications': notifications})
            except IndustryRegister.DoesNotExist:
                return render(request, 'industry/industry_notifications.html', {'error': 'No industry record found.'})
        else:
            return render(request, 'industry/industry_notifications.html', {'error': 'You are not authorized to view this page.'})
    else:
        return render(request, 'industry/industry_notifications.html', {'error': 'User is not authenticated.'})

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
    form = Feedback_Form()
    u = request.user
    if request.method == 'POST':
        form = Feedback_Form(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user=u
            obj.save()
            return redirect("view")
    return render(request,"consumer/feedback.html",{"form":form})

def view(request):
    data = Feedback.objects.filter(user = request.user)
    print(data)
    return render(request, "consumer/view.html", {"data": data})


def feedbacks(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'industry/feedbacks.html', {'feedbacks': feedbacks})


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


def profile(request, id):
    industry_register = IndustryRegister.objects.get(id=id)
    form = Industry_Profile_Form(instance=industry_register)
    if request.method == 'POST':
        form = Industry_Profile_Form(request.POST, request.FILES, instance=industry_register)
        if form.is_valid():
            form.save()
            return redirect("view_industry")


    return render(request, "industry/profile.html", {'form': form})


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
    complaints = Complaint.objects.all()
    return render(request, 'consumer/view_complaints.html', {'complaints': complaints})

def view_complaint_detail(request, complaint_id):
    # Fetch the complaint and attempt to retrieve its related response
    complaint = get_object_or_404(Complaint, id=complaint_id)
    complaint_response = ComplaintResponse.objects.filter(complaint=complaint).first()  # Fetch response if it exists

    return render(request, 'consumer/view_complaint_detail.html', {
        'complaint': complaint,
        'complaint_response': complaint_response
    })


def admin_view_complaints(request):
    complaints = Complaint.objects.all()
    return render(request, 'admin/admin_view_complaints.html', {'complaints': complaints})

def admin_view_complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    # Check if a response already exists for this complaint
    try:
        complaint_response = ComplaintResponse.objects.get(complaint=complaint)
    except ComplaintResponse.DoesNotExist:
        complaint_response = None

    if request.method == 'POST':
        response_text = request.POST.get('response')

        if complaint_response:
            # Update the existing response
            complaint_response.response = response_text
            complaint_response.response_date = timezone.now()
        else:
            # Create a new response
            complaint_response = ComplaintResponse(
                complaint=complaint,
                response=response_text,
                response_date=timezone.now()
            )

        complaint_response.save()
        messages.success(request, "Response submitted successfully.")
        return redirect('admin_view_complaints')  # Redirect to the complaints list

    return render(request, 'admin/admin_view_complaint_detail.html', {
        'complaint': complaint,
        'complaint_response': complaint_response
    })