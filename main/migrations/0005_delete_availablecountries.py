# Generated by Django 3.2.7 on 2022-08-22 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_availablecountries_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AvailableCountries',
        ),
    ]