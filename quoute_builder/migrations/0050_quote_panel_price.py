# Generated by Django 3.2.7 on 2022-09-27 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoute_builder', '0049_alter_quote_rail_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='panel_price',
            field=models.FloatField(default=0.0),
        ),
    ]