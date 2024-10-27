from django import forms
from django.contrib.auth.forms import UserCreationForm

from new_app.models import Login, IndustryRegister, ConsumerRegister, Notification, Feedback, Product, \
    Purchase, Order, Complaint


class Login_Form(UserCreationForm):
    class Meta:
        model = Login
        fields = ("username","password1","password2")

class Industry_Register_Form(forms.ModelForm):
    class Meta:
        model = IndustryRegister
        fields =('__all__')
        exclude = ('user',)

class Consumer_Register_Form(forms.ModelForm):
    class Meta:
        model = ConsumerRegister
        fields =('__all__')
        exclude = ('user',)

class Notification_Form(forms.ModelForm):
    class Meta:
        model = Notification
        fields =('__all__')
        exclude = ('user',)

class Feedback_Form(forms.ModelForm):
    class Meta:
        model = Feedback
        fields =('__all__')
        exclude = ('user',)



class Product_Form(forms.ModelForm):
    class Meta:
        model = Product
        fields =('__all__')
        exclude = ('user',)

class Purchase_Form(forms.ModelForm):
    class Meta:
        model = Purchase
        fields =('__all__')
        exclude = ('user',)


class Order_Form(forms.ModelForm):
    class Meta:
        model = Order
        fields =('__all__')
        exclude = ('user',)

class Complaint_Form(forms.ModelForm):
    class Meta:
        model = Complaint
        fields =('__all__')
        exclude = ('user',)

class Industry_Profile_Form(forms.ModelForm):
    class Meta:
        model = IndustryRegister
        fields =('__all__')
        exclude = ('user',)