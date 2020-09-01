from django.urls import path

from .views import (index, login_view, register_view, logout_view, proflie_view, delete_view)

app_name = 'account'

urlpatterns = [
    path('', index, name='home'),
    path('login/<str:user_label>', login_view, name='login'),
    path('register/<str:user_label>', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('<str:user_label>/<int:fk>/', proflie_view, name='profile'),
    path('<int:pk>/delete/', delete_view, name='delete')
]
