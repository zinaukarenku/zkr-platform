# Generated by Django 2.1.4 on 2019-01-03 23:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0030_remove_user_last_confirmation_letter_sent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organizationmember',
            options={'default_related_name': 'organization_members', 'ordering': ['order'], 'verbose_name': 'Organizacijos narys', 'verbose_name_plural': 'Organizacijos nariai'},
        ),
    ]
