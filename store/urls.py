from django.urls import path
from .views import index, cart, about, store, details, checkout, thankyou, products, orders

app_name = 'store'

urlpatterns = [
    path('', index, name='home'),
    path('store/<int:med_id>/details/', details, name='detail'),
    path('store/', store, name='store'),
    path('cart/', cart, name='cart'),
    path('about/', about, name='about'),
    path('checkout/', checkout, name='checkout'),
    path('thankyou/', thankyou, name='thankyou'),
    path('pharmacy/<int:pk>/products/', products, name='products'),
    path('pharmacy/<int:pk>/orders/', orders, name='orders')
]
