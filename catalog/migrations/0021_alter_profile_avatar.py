# Generated by Django 4.1 on 2022-10-06 12:12

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_alter_book_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=cloudinary.models.CloudinaryField(default='default.png', max_length=255, verbose_name='image'),
        ),
    ]
