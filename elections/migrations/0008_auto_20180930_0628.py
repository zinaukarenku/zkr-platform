# Generated by Django 2.1.1 on 2018-09-30 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0007_auto_20180929_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='seo_description',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
        migrations.AddField(
            model_name='election',
            name='seo_title',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
    ]
