# Generated by Django 3.2.7 on 2022-09-25 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0045_alter_productvariant_suitable_roof_style'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='availability',
        ),
        migrations.AddField(
            model_name='productvariant',
            name='availability',
            field=models.CharField(choices=[('In Stock', 'In stock'), ('Out of stock', 'Out of stock')], default=True, max_length=15),
            preserve_default=False,
        ),
    ]
