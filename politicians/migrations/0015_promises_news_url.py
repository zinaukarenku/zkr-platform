# Generated by Django 2.2.9 on 2020-01-05 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('politicians', '0014_auto_20200105_0745'),
    ]

    operations = [
        migrations.AddField(
            model_name='promises',
            name='news_url',
            field=models.URLField(blank=True, null=True, verbose_name='Pažado įgyvendinimo įrodymai'),
        ),
    ]
