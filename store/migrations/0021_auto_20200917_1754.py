# Generated by Django 3.0.8 on 2020-09-17 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_auto_20200914_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='woreda',
            field=models.IntegerField(default=0),
        ),
    ]
