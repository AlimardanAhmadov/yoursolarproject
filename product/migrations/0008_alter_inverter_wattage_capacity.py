# Generated by Django 3.2.7 on 2022-08-19 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_alter_inverter_wattage_capacity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inverter',
            name='wattage_capacity',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
    ]