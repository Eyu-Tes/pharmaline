# Generated by Django 3.0.8 on 2020-09-29 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_auto_20200917_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='rejection_reason',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]