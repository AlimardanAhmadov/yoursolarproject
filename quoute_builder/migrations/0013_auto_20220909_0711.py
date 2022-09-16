# Generated by Django 3.2.7 on 2022-09-09 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_productvariant_title'),
        ('quoute_builder', '0012_alter_quote_inverter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='inverter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selected_inverter', to='product.product'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='selected_panel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panel', to='product.product'),
        ),
    ]
