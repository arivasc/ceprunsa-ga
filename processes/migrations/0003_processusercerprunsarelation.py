# Generated by Django 4.2.16 on 2024-12-22 20:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0004_courseteacherrelation'),
        ('userAuth', '0001_initial'),
        ('processes', '0002_alter_process_dateend_alter_process_datestart'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessUserCerprunsaRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startDate', models.DateField(db_column='start_date')),
                ('endDate', models.DateField(db_column='end_date')),
                ('weekHours', models.CharField(blank=True, db_column='week_hours', max_length=7, null=True)),
                ('totalHours', models.CharField(blank=True, db_column='total_hours', max_length=7, null=True)),
                ('paymentType', models.CharField(db_column='payment_type', max_length=1)),
                ('finalState', models.CharField(db_column='final_state', default='E', max_length=1)),
                ('quality', models.CharField(default='A', max_length=1)),
                ('registerState', models.CharField(db_column='register_state', default='A', max_length=1)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='processes.process')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userAuth.roleceprunsa')),
                ('userCeprunsa', models.ForeignKey(db_column='user_ceprunsa', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'process_user_ceprunsa_relation',
            },
        ),
    ]