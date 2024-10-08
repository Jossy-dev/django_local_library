# Generated by Django 4.1 on 2022-10-06 12:45

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_alter_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]
