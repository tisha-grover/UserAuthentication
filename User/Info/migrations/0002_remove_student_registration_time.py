# Generated by Django 5.1.6 on 2025-02-27 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Info', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='registration_time',
        ),
    ]
