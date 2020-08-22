from django import forms


class OrderForm(forms.Form):
    first_name = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    order_name = forms.CharField(required=False, max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    location_description_1 = forms.CharField(label='Address / Location', max_length=100,widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Location Description'}))
    location_description_2 = forms.CharField(required=False, label='', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'House number, building name (floor and room) etc.'}))
    region = forms.CharField(max_length=25, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    woreda = forms.IntegerField(min_value=1, max_value=110, widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    phone = forms.CharField(min_length=10, max_length=13, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    order_note = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Write your notes here...'}))


class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label='', widget=forms.TextInput(
        attrs={'class':'form-control text-center', 'value': '1'}))
