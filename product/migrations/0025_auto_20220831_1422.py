# Generated by Django 3.2.7 on 2022-08-31 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0024_alter_productvariant_selected_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_type',
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='materials',
            field=models.TextField(blank=True, null=True),
        ),
    ]
