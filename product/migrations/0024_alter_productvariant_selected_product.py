# Generated by Django 3.2.7 on 2022-08-31 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0023_auto_20220831_0730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='selected_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_product', to='product.product'),
        ),
    ]