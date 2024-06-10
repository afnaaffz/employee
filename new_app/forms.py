from django import forms
from .models import Employee
import re

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def clean_emp_name(self):
        emp_name = self.cleaned_data.get('emp_name')
        if not re.match("^[A-Za-z ]*$", emp_name):
            raise forms.ValidationError("Name must not contain numbers or special characters")
        return emp_name

    def clean_designation(self):
        designation = self.cleaned_data.get('designation')
        if not re.match("^[A-Za-z ]*$", designation):
            raise forms.ValidationError("Designation must not contain numbers or special characters")
        return designation

    def clean_current_project(self):
        current_project = self.cleaned_data.get('current_project')
        if not re.match("^[A-Za-z ]*$", current_project):
            raise forms.ValidationError("Current project must not contain numbers or special characters")
        return current_project

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match("^[0-9]{10}$", phone):
            raise forms.ValidationError("Phone number must contain exactly 10 digits")
        return phone
