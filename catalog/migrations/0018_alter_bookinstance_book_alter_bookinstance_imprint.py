# Generated by Django 4.1 on 2022-09-30 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0017_alter_bookinstance_book'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinstance',
            name='book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.book'),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='imprint',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
