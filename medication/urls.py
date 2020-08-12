from django.urls import path
from .views import details


app_name = 'med'

urlpatterns = [
    path('<int:med_id>/details/', details, name='detail'),
]
