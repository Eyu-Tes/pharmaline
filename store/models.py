from django.db import models
from account.models import Pharmacy


class Medication(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    instructions = models.TextField()
    vendor = models.CharField(max_length=30)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    expiry_date = models.DateField()
    production_date = models.DateField()
    batch_number = models.CharField(max_length=100)
    requires_prescription = models.BooleanField()
    image = models.FilePathField()

    def __str__(self):
        return self.name


class Cart(models.Model):
    date = models.DateTimeField()
    user_session = models.CharField(max_length=35)

    def __str__(self):
        return self.user_session


class CartItem(models.Model):
    drug = models.ForeignKey(Medication, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField(default=0.0)

    def __str__(self):
        return self.drug.name


class Order(models.Model):
    order_name = models.CharField(unique=True, max_length=20)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    address = models.CharField(max_length=100)
    address_opt = models.CharField(max_length=100)
    region = models.CharField(max_length=25)
    woreda = models.IntegerField()
    email = models.EmailField()
    phone = models.CharField(max_length=13)
    note = models.TextField()
    cart = models.OneToOneField(Cart, on_delete=models.DO_NOTHING)
    date_time = models.DateTimeField(verbose_name='Placement Time')

    def __str(self):
        return self.order_name
