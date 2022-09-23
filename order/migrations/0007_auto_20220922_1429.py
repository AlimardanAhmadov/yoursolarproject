# Generated by Django 3.2.7 on 2022-09-22 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_orderitem_statsu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='is_paid',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='statsu',
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
