# Generated by Django 3.2.7 on 2022-08-21 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quoute_builder', '0009_quote_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='title',
            field=models.CharField(default=True, max_length=250),
            preserve_default=False,
        ),
    ]