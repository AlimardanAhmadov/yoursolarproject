# Generated by Django 3.2.7 on 2022-08-19 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_alter_inverter_wattage_capacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]