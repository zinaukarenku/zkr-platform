# Generated by Django 2.1 on 2018-08-16 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seimas', '0015_politician_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='politician',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
