from django import forms
from django.contrib.auth.forms import UserCreationForm

from new_app.models import Login, IndustryRegister, ConsumerRegister


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