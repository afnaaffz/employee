from django import forms
from django.contrib.auth.forms import UserCreationForm

from new_app.models import Login, IndustryRegister, ConsumerRegister, Feedback, Product, Order, Complaint, \
    ComplaintResponse, Payment, Meeting, RSVP, JobListing, JobApplication


class Login_Form(UserCreationForm):
    class Meta:
        model = Login
        fields = ("username","password1","password2")

class Industry_Register_Form(forms.ModelForm):
    class Meta:
        model = IndustryRegister
        fields = '__all__'  # Consider whether you really want to include all fields
        exclude = ('user',)

class Consumer_Register_Form(forms.ModelForm):
    class Meta:
        model = ConsumerRegister
        fields =('__all__')
        exclude = ('user',)


class Feedback_Form(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('industry', 'subject', 'description', 'rating')  # Include all necessary fields
        exclude = ('user',)
        widgets = {
            'rating': forms.HiddenInput(),  # Hide the rating input field
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['industry'].queryset = IndustryRegister.objects.all()  # Ensure industries are fetched correctly


class Product_Form(forms.ModelForm):
    class Meta:
        model = Product
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

class Complaint_Response_Form(forms.ModelForm):
    class Meta:
        model = ComplaintResponse
        fields =('__all__')
        exclude = ('user',)

class Complaint_Response_Form(forms.ModelForm):
    class Meta:
        model = ComplaintResponse
        fields =('__all__')
        exclude = ('user',)


class Meeting_Form(forms.ModelForm):
    class Meta:
        model = Meeting
        fields =('__all__')
        exclude = ('user',)


class RSVP_Form(forms.ModelForm):
    class Meta:
        model = RSVP
        fields =('__all__')
        exclude = ('user',)


from django import forms
from .models import JobListing

class Job_Listing_Form(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ['title', 'description', 'location']

    def clean(self):
        cleaned_data = super().clean()
        # You can add additional custom validation if needed.
        return cleaned_data

class Job_Application_Form(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'placeholder': 'Write your cover letter here...'}),
        }


