# Generated by Django 2.1.5 on 2019-02-01 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0032_auto_20190115_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='politicianinfo',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True, help_text='Indikuoja ar politiko informacija aktyvi ir galima užduoti klausimą.', verbose_name='Aktyvus'),
        ),
    ]
