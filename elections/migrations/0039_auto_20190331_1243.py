# Generated by Django 2.1.7 on 2019-03-31 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0038_auto_20190307_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='debates',
            name='type',
            field=models.IntegerField(default=1, verbose_name='Debatų tipas'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='debates',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=7, help_text='Google žemėlapiams', max_digits=10, verbose_name='Platuma'),
        ),
        migrations.AlterField(
            model_name='debates',
            name='lng',
            field=models.DecimalField(blank=True, decimal_places=7, help_text='Google žemėlapiams', max_digits=10, verbose_name='Ilguma'),
        ),
    ]
