# Generated by Django 3.2.7 on 2022-09-25 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0019_alter_order_created'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-id']},
        ),
    ]
