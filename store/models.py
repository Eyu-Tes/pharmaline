from django.db import models
from account.models import Pharmacy


class Medication(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    instructions = models.TextField()
    vendor = models.CharField(max_length=30)
    pharmacy_id = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
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
    drug_id = models.ForeignKey(Medication, on_delete=models.CASCADE)
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE)
