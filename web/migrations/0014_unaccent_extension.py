# Generated by Django 2.1.1 on 2018-10-10 19:57

from django.conf import settings
from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_politicianinfo_user'),
    ]

    operations = [
        UnaccentExtension()
    ]