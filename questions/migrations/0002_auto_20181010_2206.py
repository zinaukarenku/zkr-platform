# Generated by Django 2.1.1 on 2018-10-10 19:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('web', '0011_politicianinfo'),
        ('questions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='politician',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='questions', to='web.PoliticianInfo'),
        ),
        migrations.AddField(
            model_name='answer',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='question_answers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='question', to='questions.Question'),
        ),
    ]
