import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Medication


class OrderForm(forms.Form):
    first_name = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=15, widget=forms.TextInput(
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
        attrs={'class': 'form-control text-center', 'value': '1'}),
        error_messages={'invalid': 'Make sure you insert a number here.'})
    med_stock_count = None

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity > self.med_stock_count:
            raise ValidationError(f'The pharmacy only has {self.med_stock_count}.')
        return quantity


class ProductForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ('batch_number', 'name', 'vendor', 'description', 'instructions', 'price', 'stock',
                  'production_date', 'expiry_date', 'requires_prescription', 'image')

        widgets = {
            'batch_number': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 5}),
            'instructions': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'production_date': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'expiry_date': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            # 'requires_prescription': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['batch_number'].widget.attrs.update({'autofocus': 'autofocus'})
