# Generated by Django 3.2.7 on 2022-09-01 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0015_auto_20220901_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='grand_total_currency',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='total_cost_currency',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='price_currency',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='total_cost_currency',
        ),
        migrations.AlterField(
            model_name='cart',
            name='grand_total',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='cart',
            name='total_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='price',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='total_cost',
            field=models.FloatField(default=0.0),
        ),
    ]