# Generated by Django 4.2.16 on 2025-02-04 00:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processes', '0004_remove_processusercerprunsarelation_course_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('observation', models.TextField()),
                ('document', models.FileField(blank=True, null=True, upload_to='observations/')),
                ('registerState', models.CharField(db_column='register_state', default='A', max_length=1)),
                ('idProcessUserCeprunsaRelation', models.ForeignKey(db_column='id_process_user_ceprunsa_relation', on_delete=django.db.models.deletion.CASCADE, to='processes.processusercerprunsarelation')),
                ('registerBy', models.ForeignKey(db_column='register_by', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'observations',
            },
        ),
    ]
