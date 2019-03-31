# Generated by Django 2.1.7 on 2019-03-31 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0039_auto_20190331_1243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='debates',
            name='type',
        ),
        migrations.AddField(
            model_name='debates',
            name='election_type',
            field=models.IntegerField(choices=[(1, 'Merų rinkimai'), (2, 'Seimo rinkimai'), (3, 'Europos Parlamento rinkimai'), (4, 'Prezidento rinkimai'), (5, 'Savivaldos tarybų rinkimai')], default=1, verbose_name='Rinkimų tipas'),
            preserve_default=False,
        ),
    ]
