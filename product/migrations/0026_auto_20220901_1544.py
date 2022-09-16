# Generated by Django 3.2.7 on 2022-09-01 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_auto_20220831_1422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='primary_discount_currency',
        ),
        migrations.RemoveField(
            model_name='product',
            name='primary_price_currency',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='discount_currency',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='price_currency',
        ),
        migrations.AlterField(
            model_name='product',
            name='primary_discount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='product',
            name='primary_price',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='discount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='price',
            field=models.FloatField(default=0.0),
        ),
    ]