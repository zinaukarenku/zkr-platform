# Generated by Django 2.1.1 on 2018-12-03 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0022_auto_20181202_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationmember',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='web.OrganizationMemberGroup'),
        ),
        migrations.AlterField(
            model_name='organizationmember',
            name='role',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Nario rolė'),
        ),
    ]
