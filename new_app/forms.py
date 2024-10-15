from django import forms
from django.contrib.auth.forms import UserCreationForm

from new_app.models import Login, IndustryRegister, ConsumerRegister, Notification, Feedback, IndustryProfile, Product


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

class Industry_Profile_Form(forms.ModelForm):
    class Meta:
        model = IndustryProfile
        fields =('__all__')
        exclude = ('user',)

class Product_Form(forms.ModelForm):
    class Meta:
        model = Product
        fields =('__all__')
        exclude = ('user',)