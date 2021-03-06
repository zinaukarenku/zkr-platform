# Generated by Django 2.2.9 on 2020-01-04 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('politicians', '0006_remove_promiseaction_politician'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promises',
            name='total_score',
        ),
        migrations.AlterField(
            model_name='promiseaction',
            name='promise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promise_action', to='politicians.Promises'),
        ),
        migrations.AlterField(
            model_name='promises',
            name='politician',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promises', to='politicians.Politicians'),
        ),
    ]
