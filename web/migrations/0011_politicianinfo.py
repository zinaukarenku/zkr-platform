# Generated by Django 2.1.1 on 2018-10-10 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seimas', '0026_auto_20180905_1132'),
        ('web', '0010_auto_20181002_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoliticianInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('seimas_politician', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='seimas.Politician')),
            ],
            options={
                'verbose_name_plural': 'Politician information',
                'ordering': ['-created_at', 'name'],
            },
        ),
    ]
