from django.urls import path
from .views import index, cart, about


app_name = 'store'

urlpatterns = [
    path('', index, name='home'),
    path('cart/', cart, name='cart'),
    path('about/', about, name='about')
]
