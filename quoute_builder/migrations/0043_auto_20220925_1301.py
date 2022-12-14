# Generated by Django 3.2.7 on 2022-09-25 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0046_auto_20220925_1220'),
        ('quoute_builder', '0042_auto_20220925_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='fitting',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='selected_fitting', to='product.productvariant'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='inverter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='selected_inverter', to='product.productvariant'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='selected_panel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='panel', to='product.productvariant'),
        ),
    ]
