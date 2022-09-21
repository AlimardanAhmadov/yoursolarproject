# Generated by Django 3.2.7 on 2022-09-19 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoute_builder', '0034_auto_20220919_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='shipping_price',
            field=models.FloatField(default=200.0),
        ),
        migrations.AlterField(
            model_name='quote',
            name='cable_length_panel_cons',
            field=models.FloatField(blank=True, null=True, verbose_name='Cable length from panels to the consumer unit via the Inverter'),
        ),
    ]
