# Generated by Django 2.1.4 on 2019-02-02 22:56

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0022_auto_20190202_2140'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='debates',
            managers=[
                ('debate_active', django.db.models.manager.Manager()),
            ],
        ),
    ]
