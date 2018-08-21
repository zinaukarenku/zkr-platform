# Generated by Django 2.1 on 2018-08-20 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seimas', '0022_auto_20180816_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='politiciangame',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='politician_games', to=settings.AUTH_USER_MODEL),
        ),
    ]
