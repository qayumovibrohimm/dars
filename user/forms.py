from django import forms
from django.forms import PasswordInput

from .models import CustomUser



class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)




class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password']