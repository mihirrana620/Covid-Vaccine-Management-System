# Generated by Django 3.1.3 on 2023-04-29 05:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('covidvaccinemanagement', '0007_vaccineappointmentdetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vaccineappointmentdetails',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
