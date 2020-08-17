from django.urls import path

from .views import (index, login_view, register_view, logout_view)

app_name = 'account'

urlpatterns = [
    path('', index, name='home'),
    path('login/<str:user_label>', login_view, name='login'),
    path('register/<str:user_label>', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]
