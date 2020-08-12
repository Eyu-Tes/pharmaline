from django.urls import path

from .views import (
    index, customer_login_view, customer_register_view,
    pharmacy_login_view, pharmacy_register_view, logout_view)

app_name = 'account'

urlpatterns = [
    path('', index, name='home'),
    path('customer/login/', customer_login_view, name='customer-login'),
    path('custom/register/', customer_register_view, name='customer-register'),
    path('pharmacy/login/', pharmacy_login_view, name='pharmacy-login'),
    path('pharmacy/register/', pharmacy_register_view, name='pharmacy-register'),
    path('logout/', logout_view, name='logout'),
]
