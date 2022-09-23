# Generated by Django 3.2.7 on 2022-09-23 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('order', '0008_order_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='secondary_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='model_type',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='object_id',
            field=models.PositiveIntegerField(default=True),
            preserve_default=False,
        ),
    ]
