# Generated by Django 3.2.7 on 2022-08-21 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_auto_20220815_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]