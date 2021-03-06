from enum import Enum

import os.path

import shortuuid
from django.conf import settings
from django.db import models

from account.models import Customer, Pharmacy


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
    image = models.ImageField(upload_to=f'products/', default='default_med.png')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    # Silents - UnorderedObjectListWarning: Pagination may yield inconsistent results ...
    class Meta:
        ordering = ['id']


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

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.drug.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.drug.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    address = models.CharField(max_length=100)
    address_opt = models.CharField(max_length=100)
    region = models.CharField(max_length=25)
    woreda = models.IntegerField(default=0)
    email = models.EmailField()
    phone = models.CharField(max_length=13)
    note = models.TextField()
    cart = models.OneToOneField(Cart, on_delete=models.DO_NOTHING)
    date_time = models.DateTimeField(verbose_name='Placement Time')

    PRESCRIPTIONS_DIR_NAME = 'prescriptions'

    def __str(self):
        return str(self.customer) + ' ' + self.address

    def save_prescription_image(self, image):
        save_path = os.path.join(settings.MEDIA_ROOT, self.PRESCRIPTIONS_DIR_NAME, str(self.pk))
        os.makedirs(save_path, exist_ok=True)
        image_extension = image.name[image.name.rindex('.'):]
        file_path = os.path.join(save_path, shortuuid.random(length=10) + image_extension)
        with open(file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

    def get_prescription_images(self):
        pass


class EFDA(models.Model):
    batch_number = models.CharField(max_length=35, unique=True)
    expiry_date = models.DateTimeField()
    in_use = models.BooleanField(default=False)
    med_id = models.ForeignKey(Medication, on_delete=models.SET_NULL, null=True)


class OrderStatus(Enum):
    PENDING = 'pending'
    DISPATCHED = 'dispatched'
    COMPLETE = 'complete'
    REJECTED = 'rejected'
    CANCELED = 'canceled'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cart_item = models.OneToOneField(CartItem, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default=OrderStatus.PENDING.value)
    rejection_reason = models.TextField()