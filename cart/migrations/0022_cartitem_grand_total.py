# Generated by Django 3.2.7 on 2022-09-04 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0021_remove_cart_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='grand_total',
            field=models.FloatField(default=0.0),
        ),
    ]
