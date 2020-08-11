from django.db import models


class Pharmacy(models.Model):
    pass


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
