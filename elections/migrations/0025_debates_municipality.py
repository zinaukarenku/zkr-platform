# Generated by Django 2.1.4 on 2019-02-03 00:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0035_auto_20190201_2156'),
        ('elections', '0024_auto_20190202_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='debates',
            name='municipality',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.Municipality'),
            preserve_default=False,
        ),
    ]
