# Generated by Django 2.1.1 on 2018-12-07 13:34

from django.db import migrations, models
import elections.models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0011_auto_20181207_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presidentcandidate',
            name='photo',
            field=models.ImageField(upload_to=elections.models.PresidentCandidate._candidate_photo_file, verbose_name='Kandidato nuotrauka'),
        ),
    ]
