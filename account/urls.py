from django.urls import path

from .views import (index, login_view, customer_register_view, logout_view)

app_name = 'account'

urlpatterns = [
    path('', index, name='home'),
    path('login/<str:customer_label>', login_view, name='login'),
    path('customer/register/', customer_register_view, name='customer-register'),
    path('logout/', logout_view, name='logout'),
]
