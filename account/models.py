from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    phone = models.CharField(max_length=20, verbose_name='phone number')
    disabled = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'account_customer'

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Pharmacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=35)
    phone = models.CharField(max_length=20, verbose_name='phone number')
    location = models.CharField(max_length=100)
    disabled = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'account_pharmacy'

    def __str__(self):
        return f'{self.pharmacy_name}'
