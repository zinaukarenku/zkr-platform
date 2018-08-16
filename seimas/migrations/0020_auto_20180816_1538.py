# Generated by Django 2.1 on 2018-08-16 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seimas', '0019_auto_20180816_1529'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='politicianterm',
            name='elected_by_list',
        ),
        migrations.AddField(
            model_name='politicianterm',
            name='election_type',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='politician_terms', to='seimas.ElectionType'),
            preserve_default=False,
        ),
    ]
