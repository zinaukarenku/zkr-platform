# Generated by Django 2.1.7 on 2019-05-21 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0052_europarliamentcandidateconviction_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='presidentcandidate',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True, help_text='Indikuoja ar kandidatas į prezidentus matomas prezidenų sąraše bei galima užduoti naują klausimą.', verbose_name='Aktyvus'),
        ),
    ]
