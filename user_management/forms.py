# user_management/forms.py
from django import forms
from .models import CustomUser, Therapist
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'company_name', 'legal_name', 'profile_pic', 'password']

class TherapistRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'company_name', 'legal_name', 'profile_pic', 'password']

class TherapistDetailsForm(forms.ModelForm):
    class Meta:
        model = Therapist
        fields = ['name', 'years_of_experience', 'expertise', 'license_certificate']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'company_name', 'legal_name', 'profile_pic']