# Generated by Django 2.1 on 2018-08-13 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seimas', '0010_auto_20180813_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='politicianbusinesstrip',
            name='is_secondment',
            field=models.BooleanField(default=False, verbose_name='True stands for Komandiruotė, False for Kelionė'),
        ),
    ]
