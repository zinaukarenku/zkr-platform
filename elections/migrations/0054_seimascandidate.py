# Generated by Django 2.2.14 on 2020-08-07 16:37

from django.db import migrations, models
import django_resized.forms
import elections.models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0053_presidentcandidate_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeimasCandidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Indikuoja ar kandidatas į matomas sąraše bei galima užduoti naują klausimą.', verbose_name='Aktyvus')),
                ('name', models.CharField(max_length=256, verbose_name='Kandidato vardas ir pavardė')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Kandidato el. paštas')),
                ('slug', models.SlugField(editable=False, unique=True)),
                ('photo', django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format=None, keep_meta=False, null=True, quality=90, size=[256, 256], upload_to=elections.models.SeimasCandidate._candidate_photo_file, verbose_name='Kandidato nuotrauka')),
                ('party', models.CharField(blank=True, max_length=256, null=True, verbose_name='Iškėlusi partija arba rinkiminis komitetas')),
                ('district', models.CharField(blank=True, max_length=256, null=True, verbose_name='Apygarda')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Sukurta')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atnaujinta')),
            ],
            options={
                'verbose_name': 'Kandidatas į seimą',
                'verbose_name_plural': 'Kandidatai į seimą',
            },
        ),
    ]
