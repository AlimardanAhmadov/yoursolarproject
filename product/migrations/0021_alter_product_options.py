# Generated by Django 3.2.7 on 2022-08-29 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_alter_product_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-id'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
    ]
