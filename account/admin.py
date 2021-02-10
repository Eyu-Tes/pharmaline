from django.contrib import admin
from django.contrib.auth.models import User
from .models import Customer, Pharmacy, PharmaAdmin

# Register your models here.
admin.site.register(Customer)
admin.site.register(Pharmacy)
admin.site.register(Customer)
