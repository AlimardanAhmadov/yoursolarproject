# Generated by Django 3.2.7 on 2022-09-25 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoute_builder', '0045_quote_inverter'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]