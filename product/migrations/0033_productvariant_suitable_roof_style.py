# Generated by Django 3.2.7 on 2022-09-18 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0032_auto_20220917_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='suitable_roof_style',
            field=models.CharField(blank=True, help_text='For Hooks/Fittings', max_length=10, null=True),
        ),
    ]
