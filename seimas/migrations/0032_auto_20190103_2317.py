# Generated by Django 2.1.4 on 2019-01-03 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seimas', '0031_auto_20190103_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee',
            name='slug',
            field=models.SlugField(max_length=128, unique=True),
        ),
    ]
