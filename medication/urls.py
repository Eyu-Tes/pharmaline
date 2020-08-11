from django.urls import path
from .views import details


urlpatterns = [
    path('<int:med_id>/details/', details, name='med-detail'),
]
