# Generated by Django 3.2.7 on 2022-08-18 11:26

from django.db import migrations, models
import django.db.models.deletion
import product.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_alter_product_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(default='default.png', upload_to=product.models.image_directory_path)),
            ],
            options={
                'verbose_name': 'ProductImage',
                'verbose_name_plural': 'ProductImages',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='cost',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ProductVariant',
        ),
        migrations.AddField(
            model_name='productimage',
            name='selected_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddIndex(
            model_name='productimage',
            index=models.Index(fields=['selected_product', 'id'], name='product_pro_selecte_1561a0_idx'),
        ),
    ]
