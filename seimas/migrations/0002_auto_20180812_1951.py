# Generated by Django 2.1 on 2018-08-12 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seimas', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='party',
            options={'verbose_name_plural': 'Parties'},
        ),
        migrations.AlterModelOptions(
            name='politician',
            options={'verbose_name_plural': 'Politicians'},
        ),
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ['term', 'number'], 'verbose_name_plural': 'Sessions'},
        ),
        migrations.AlterModelOptions(
            name='term',
            options={'ordering': ['start'], 'verbose_name_plural': 'Terms'},
        ),
        migrations.RemoveField(
            model_name='politician',
            name='sessions',
        ),
        migrations.AddField(
            model_name='politician',
            name='terms',
            field=models.ManyToManyField(related_name='politicians', to='seimas.Term'),
        ),
    ]
