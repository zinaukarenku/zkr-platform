# Generated by Django 2.1.1 on 2018-10-10 19:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_auto_20181010_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='politicianinfo',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='politician_info', to=settings.AUTH_USER_MODEL),
        ),
    ]
