# Generated by Django 3.2.7 on 2022-08-23 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_productvariant_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
