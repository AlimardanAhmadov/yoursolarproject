# Generated by Django 3.2.7 on 2022-09-22 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_alter_orderitem_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='statsu',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]