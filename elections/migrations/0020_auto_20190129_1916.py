# Generated by Django 2.1.5 on 2019-01-29 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0019_mayorcandidate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mayorcandidate',
            name='party',
            field=models.CharField(blank=True, max_length=256, verbose_name='Iškėlusi partija arba rinkiminis komitetas'),
        ),
    ]
