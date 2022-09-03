# Generated by Django 3.2.7 on 2022-09-02 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_auto_20220901_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='image_url',
        ),
        migrations.AddField(
            model_name='product',
            name='primary_image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
