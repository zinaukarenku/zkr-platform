# Generated by Django 2.2.9 on 2020-01-05 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('politicians', '0012_promiseaction_attachment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='politicians',
            name='office',
        ),
        migrations.AddField(
            model_name='experience',
            name='politician',
            field=models.ForeignKey(default='2', on_delete=django.db.models.deletion.CASCADE, related_name='experience', to='politicians.Politicians'),
            preserve_default=False,
        ),
    ]
