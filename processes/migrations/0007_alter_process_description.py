# Generated by Django 4.2.16 on 2025-02-24 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processes', '0006_alter_process_registerstate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='description',
            field=models.TextField(),
        ),
    ]
