from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Customer, Pharmacy, PharmaAdmin


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'] = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm'}), label='Password')
        self.fields['password2'] = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm'}), label='Confirm password')
        self.fields['username'].widget.attrs.pop("autofocus", None)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("This field is required.")
        if User.objects.filter(email=email):
            raise ValidationError("A user with that email already exists.")
        return email


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-sm'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': 'autofocus'})


class CustomerProfileForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', }),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }


class PharmacyProfileForm(ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['pharmacy_name', 'phone', 'location']

        widgets = {
            'pharmacy_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', }),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'location': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }


class PharmaAdminProfileForm(ModelForm):
    class Meta:
        model = PharmaAdmin
        fields = ['first_name', 'last_name', 'phone']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', }),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }


class UpdateUserForm(ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            # 'id': forms.HiddenInput(),
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def clean_email(self):
        user_id = self.data.get('id')
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("This field is required.")
        # Check that updated email is unique, by comparing with existing emails
        # But don't include the existing email of the current user in the update from
        if User.objects.filter(email=email).exclude(id=user_id):
            raise ValidationError("A user with that email already exists.")
        return email


class RequestUserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            self.add_error('email', "There is no user with this email.")
        return email


class ConfirmUserPasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(label="New password",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))
    new_password2 = forms.CharField(label="New password confirmation",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Old password",
                                   widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))
    new_password1 = forms.CharField(label="New password",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))
    new_password2 = forms.CharField(label="New password confirmation",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))
