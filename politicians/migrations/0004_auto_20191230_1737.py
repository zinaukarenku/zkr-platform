# Generated by Django 2.2.9 on 2019-12-30 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('politicians', '0003_auto_20191230_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promises',
            name='politician',
        ),
        migrations.AddField(
            model_name='promises',
            name='politician',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='politicians.Politicians'),
            preserve_default=False,
        ),
    ]
