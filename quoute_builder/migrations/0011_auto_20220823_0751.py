# Generated by Django 3.2.7 on 2022-08-23 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoute_builder', '0010_quote_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='shipping_price',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='quote',
            name='tax',
            field=models.FloatField(default=0.0),
        ),
    ]
