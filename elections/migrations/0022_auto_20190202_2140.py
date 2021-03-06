# Generated by Django 2.1.4 on 2019-02-02 21:40

from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms
import elections.models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0021_auto_20190201_2127'),
    ]

    operations = [
        migrations.CreateModel(
            name='Debates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debate_name', models.CharField(max_length=256, verbose_name='Debatų pavadinimas')),
                ('debate_location', models.CharField(max_length=256, verbose_name='Debatų vieta (miestas arba renginio vieta)')),
                ('debate_lat', models.DecimalField(decimal_places=6, max_digits=8, verbose_name='Platuma (Google žemėlapiams)')),
                ('debate_lng', models.DecimalField(decimal_places=6, max_digits=8, verbose_name='Ilguma (Google žemėlapiams)')),
                ('debate_date', models.DateField(verbose_name='Debatų data')),
                ('debate_time', models.TimeField(verbose_name='Debatų laikas')),
                ('debate_facebook_url', models.URLField(blank=True, verbose_name='Debatų Facebook Event puslapio url')),
            ],
            options={
                'verbose_name': 'Debatai',
            },
        ),
        migrations.CreateModel(
            name='Moderators',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=256, verbose_name='Moderatoriaus vardas')),
                ('last_name', models.CharField(max_length=256, verbose_name='Moderatoriaus pavardė')),
                ('photo', django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format=None, keep_meta=False, null=True, quality=90, size=[256, 256], upload_to=elections.models.Moderators._moderator_photo_file, verbose_name='Moderatoriaus nuotrauka')),
            ],
            options={
                'verbose_name': 'Moderatoriai',
            },
        ),
        migrations.AddField(
            model_name='debates',
            name='debate_moderator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.Moderators'),
        ),
    ]
