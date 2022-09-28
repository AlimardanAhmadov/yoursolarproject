# Generated by Django 3.2.7 on 2022-09-23 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_auto_20220923_1010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='model_type',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='object_id',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_category',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_title',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]