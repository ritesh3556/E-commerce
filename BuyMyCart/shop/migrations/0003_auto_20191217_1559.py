# Generated by Django 2.2.4 on 2019-12-17 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20191213_2229'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='catogory_name',
            new_name='category_name',
        ),
    ]
