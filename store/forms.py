from django import forms
from django.core.exceptions import ValidationError

import re


class OrderForm(forms.Form):
    first_name = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    order_name = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    location_description_1 = forms.CharField(label='Address / Location', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Location Description'}))
    location_description_2 = forms.CharField(required=False, label='', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'House number, building name (floor and room) etc.'}))
    region = forms.CharField(max_length=25, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Addis Ababa, etc.'}))
    woreda = forms.IntegerField(min_value=1, max_value=110, widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'address@example.com'}))
    phone = forms.CharField(min_length=10, max_length=13, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    order_note = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Write your notes here...'}))
    order_requires_prescription = False
    prescriptions = forms.ImageField(required=False, widget=forms.ClearableFileInput(
        attrs={'class': 'form-control', 'multiple': True}))

    def clean_phone(self):
        phone_number = self.cleaned_data['phone']
        if not re.match('(\\+?251|0)[91]\\d{8}', phone_number):
            self.add_error('phone', 'Invalid phone number.')
        return phone_number

    def clean_prescriptions(self):
        prescriptions = self.cleaned_data['prescriptions']

        if self.order_requires_prescription and not prescriptions:
            raise ValidationError('A prescription(s) must be uploaded for the selected medication.')
        return prescriptions


class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label='', widget=forms.TextInput(
        attrs={'class': 'form-control text-center', 'value': '1'}))
