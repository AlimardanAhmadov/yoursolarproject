# Generated by Django 3.2.7 on 2022-12-10 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0052_auto_20221210_1516'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productvariant',
            old_name='cabel_size',
            new_name='cable_size',
        ),
    ]