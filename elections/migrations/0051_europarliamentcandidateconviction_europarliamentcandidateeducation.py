# Generated by Django 2.1.7 on 2019-05-12 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0050_auto_20190511_1819'),
    ]

    operations = [
        migrations.CreateModel(
            name='EuroParliamentCandidateConviction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, max_length=250, verbose_name='Nuosprendžio tekstas')),
                ('court', models.CharField(blank=True, max_length=150, verbose_name='Institucija')),
                ('year', models.DateField(blank=True, null=True, verbose_name='Nuosprendžio metai')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Sukurta')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atnaujinta')),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conviction', to='elections.EuroParliamentCandidate')),
            ],
            options={
                'verbose_name': 'Teistumo įrašas',
                'verbose_name_plural': 'Teistumo įrašai',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='EuroParliamentCandidateEducation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edu_type', models.IntegerField(blank=True, choices=[(1, 'Vidurinis'), (2, 'Aukštasis universitetinis'), (3, 'Aukštasis neuniversitetinis')], null=True, verbose_name='Išsilavinimo tipas')),
                ('school', models.CharField(blank=True, max_length=250, verbose_name='Mokykla/Universitetas')),
                ('degree', models.CharField(blank=True, max_length=250, verbose_name='Mokslo laipsnis')),
                ('speciality', models.CharField(blank=True, max_length=250, verbose_name='Specialybė')),
                ('grad_year', models.DateField(blank=True, null=True, verbose_name='Baigimo metai')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Sukurta')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atnaujinta')),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='elections.EuroParliamentCandidate')),
            ],
            options={
                'verbose_name': 'Išsilavinimo įrašas',
                'verbose_name_plural': 'Išsilavinimo įrašai',
                'ordering': ['created_at'],
            },
        ),
    ]
