# Generated by Django 3.2.7 on 2022-09-25 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quoute_builder', '0040_auto_20220920_1538'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quote',
            name='fitting',
        ),
        migrations.RemoveField(
            model_name='quote',
            name='inverter',
        ),
    ]
