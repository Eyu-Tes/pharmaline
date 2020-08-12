from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Customer, Pharmacy


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'] = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm'}), label='Password')
        self.fields['password2'] = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm'}), label='Confirm password')


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-sm'}))


class CustomerProfileForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }


class PharmacyProfileForm(ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['pharmacy_name', 'email', 'phone', 'location']

        widgets = {
            'pharmacy_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'location': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
