from django.urls import path
from .views import index, cart, about, store, checkout, thankyou


app_name = 'store'

urlpatterns = [
    path('', index, name='home'),
    path('store/', store, name='store'),
    path('cart/', cart, name='cart'),
    path('about/', about, name='about'),
    path('checkout/', checkout, name='checkout'),
    path('thankyou/', thankyou, name='thankyou')
]
