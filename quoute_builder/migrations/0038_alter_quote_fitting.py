# Generated by Django 3.2.7 on 2022-09-19 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0033_productvariant_suitable_roof_style'),
        ('quoute_builder', '0037_alter_quote_fitting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='fitting',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.CASCADE, related_name='selected_fitting', to='product.productvariant'),
            preserve_default=False,
        ),
    ]
