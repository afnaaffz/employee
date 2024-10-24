from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404

from new_app.forms import Login_Form, Consumer_Register_Form, Industry_Register_Form, Notification_Form, Feedback_Form, \
    Product_Form
from new_app.models import ConsumerRegister, IndustryRegister, Login, Notification, Feedback, Product, Purchase, Order


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

def admin_view_consumer(request):
    data = ConsumerRegister.objects.filter(user__is_approved=False)
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
            a = form1.save(commit=False)
            a.is_industry = True
            a.save()
            user1 = form2.save(commit=False)
            user1.user = a
            user1.save()
            return redirect("login")
    return render(request,"industry/industry.html", {'form1':form1, 'form2':form2})


def view_industry(request):
    data = IndustryRegister.objects.all()
    return render(request, "industry/view_industry.html", {'data': data})


def consumer_view_industry(request):
    # Get distinct locations
    locations = IndustryRegister.objects.values_list('location', flat=True).distinct()

    # Get the selected location from the dropdown
    selected_location = request.GET.get('location')

    # Filter the data based on the selected location
    if selected_location:
        data = IndustryRegister.objects.filter(location=selected_location)
    else:
        data = IndustryRegister.objects.all()

    return render(request, "consumer/consumer_view_industry.html", {
        'data': data,
        'locations': locations,  # Pass the list of locations to the template
        'selected_location': selected_location,  # Pass the selected location to the template
    })


def add_industry(request):
    form = Industry_Register_Form()
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST)
        if form.is_valid():
            form.save()
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

    return render(request, "admin/update_product.html", {'form': form})

def delete_industry(request, id):
    industry = get_object_or_404(IndustryRegister, id=id)
    industry.delete()
    return redirect('admin_view_industry')


# Admin approves industry user
def approve_industry(request, user_id):
    user = get_object_or_404(Login, pk=user_id)
    if not user.is_approved:
        user.is_approved = True
        user.is_rejected = False
        user.save()
        messages.success(request, f'{user.username} has been approved.')
    return redirect('admin_view_industry')

# Admin rejects industry user
def reject_industry(request, user_id):
    user = get_object_or_404(Login, pk=user_id)
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



def add_notifications(request):
    form = Notification_Form()
    if request.method == 'POST':
        form = Notification_Form(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_view_notifications")
    return render(request, 'admin/add_notifications.html', {'form': form})

def admin_view_notifications(request):
    data = Notification.objects.all()
    return render(request, "admin/admin_view_notifications.html", {'data': data})



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