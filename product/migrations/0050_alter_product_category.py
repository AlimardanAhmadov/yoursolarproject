# Generated by Django 3.2.7 on 2022-10-06 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0049_alter_productvariant_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('Inverter', 'Inverter'), ('Panel', 'Panel'), ('Rails & Clips', 'Rails & Clips'), ('Fitting', 'Fitting'), ('Battery', 'Battery'), ('Other', 'Other')], max_length=50),
        ),
    ]
