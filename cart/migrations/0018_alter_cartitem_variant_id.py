# Generated by Django 3.2.7 on 2022-09-01 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0017_cartitem_variant_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='variant_id',
            field=models.CharField(default=True, max_length=250),
            preserve_default=False,
        ),
    ]
