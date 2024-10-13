from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404

from new_app.forms import Login_Form, Consumer_Register_Form, Industry_Register_Form
from new_app.models import ConsumerRegister, IndustryRegister, Login


# Create your views here.

def index(request):
    return render(request,"index.html")

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

def adminbase(request):
    return render(request,"admin/admin base.html")

def admin_view_consumer(request):
    # Fetch all consumers (approved, rejected, or awaiting approval)
    data = ConsumerRegister.objects.select_related('user').all()
    return render(request, "admin/admin_view_consumers.html", {'data': data})
def admin_view_industry(request):
    # Fetch all industries (approved, rejected, or awaiting approval)
    data = IndustryRegister.objects.select_related('user').all()
    return render(request, "admin/admin_view_industry.html", {'data': data})

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
    print(data)
    return render(request,"industry/view_industry.html",{'data':data})


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
    return render(request,"consumer/view_consumer.html",{'data':data})


def add_industry(request):
    form = Industry_Register_Form()
    if request.method == 'POST':
        form = Industry_Register_Form(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the industry view page after adding data
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

    return render(request, "admin/update_industry.html", {'form': form})

def delete_industry(request, id):
    industry = get_object_or_404(IndustryRegister, id=id)
    industry.delete()
    return redirect('admin_view_industry')


# Admin approves industry user
def approve_industry(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"Industry {user.username} has been approved.")
    return redirect('admin_view_industry')

# Admin rejects industry user
def reject_industry(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    user.is_rejected = True  # Update rejection status
    user.save()
    messages.success(request, f"Industry {user.username} has been rejected.")
    return redirect('admin_view_industry')

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
    user.is_rejected = True  # Update rejection status
    user.save()
    messages.success(request, f"Consumer {user.username} has been rejected.")
    return redirect('admin_view_consumer')

def admin_view_industry(request):
    # Fetch all industries that are not yet approved
    data = IndustryRegister.objects.filter(user__is_approved=False)
    return render(request, "admin/admin_view_industry.html", {'data': data})

def admin_view_consumer(request):
    # Fetch all consumers that are not yet approved
    data = ConsumerRegister.objects.filter(user__is_approved=False)
    return render(request, "admin/admin_view_consumers.html", {'data': data})
