# Generated by Django 3.2.7 on 2022-09-27 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoute_builder', '0046_quote_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='no_rails',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Quantity of rails'),
        ),
        migrations.AddField(
            model_name='quote',
            name='rail_price',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Total rail cost'),
        ),
    ]
