from django.urls import path
from .views import index, cart, about, store, search, details, checkout, thankyou, products, orders, order_details

app_name = 'store'

urlpatterns = [
    path('', index, name='home'),
    path('store/<int:med_id>/details/', details, name='detail'),
    path('store/<int:page_num>', store, name='store'),
    path('store/search/', search, name='search'),
    path('cart/', cart, name='cart'),
    path('about/', about, name='about'),
    path('checkout/', checkout, name='checkout'),
    path('thankyou/', thankyou, name='thankyou'),
    path('pharmacy/<int:pk>/products/', products, name='products'),
    path('pharmacy/<int:pk>/orders/', orders, name='orders'),
    path('pharmacy/orders/<int:pk>/', order_details, name='order_details')
]
