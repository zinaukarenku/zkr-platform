# Generated by Django 2.2.9 on 2020-01-05 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('politicians', '0013_auto_20200105_0553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='politicians',
            name='asm_id',
            field=models.IntegerField(blank=True, help_text='Asmens id is used internally in seimas web', null=True, unique=True),
        ),
    ]
