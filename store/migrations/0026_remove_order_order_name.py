# Generated by Django 3.0.8 on 2020-10-12 19:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_medication_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_name',
        ),
    ]
