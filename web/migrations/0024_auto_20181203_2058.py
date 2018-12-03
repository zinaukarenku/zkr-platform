# Generated by Django 2.1.1 on 2018-12-03 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0023_auto_20181203_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationmember',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Jei vartotojas nėra priskiriamas, jokiai grupei jis bus rodomas tik regioninėje grupėje.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='web.OrganizationMemberGroup'),
        ),
    ]
