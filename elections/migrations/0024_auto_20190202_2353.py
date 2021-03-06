# Generated by Django 2.1.4 on 2019-02-02 23:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0023_auto_20190202_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='debates',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Sukurta'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='debates',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Atnaujinta'),
        ),
    ]
