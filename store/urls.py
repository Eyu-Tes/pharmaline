from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (index, cart, about, store, search, detail, checkout, thankyou, products, orders, order_details,
                    pharma_admin_home, user_list, create_product, update_product, delete_product, toggle_active_product)

app_name = 'store'

urlpatterns = [
    path('', index, name='home'),
    path('store/details/<int:med_id>', detail, name='detail'),
    path('store/<int:page_num>', store, name='store'),
    path('store/search/', search, name='search'),
    path('cart/', cart, name='cart'),
    path('about/', about, name='about'),
    path('checkout/', checkout, name='checkout'),
    path('thankyou/', thankyou, name='thankyou'),
    path('products/', products, name='products'),
    path('orders/details/<int:pk>/', order_details, name='order_details'),
    path('orders/<str:status>', orders, name='orders'),
    path('pharma_admin/', pharma_admin_home, name='pharma_admin_home'),
    path('list/<str:user_label>/', user_list, name='user_list'),
    path('pharmacy/<int:pk>/product/create/', create_product, name='product_create'),
    path('pharmacy/<int:pk>/product/<int:prod_id>/update/', update_product, name='product_update'),
    path('pharmacy/<int:pk>/product/<int:prod_id>/delete/', delete_product, name='product_delete'),
    path('product/toggle/status/', toggle_active_product, name='product_toggle_active'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
