# Generated by Django 3.1.3 on 2023-05-02 08:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('covidvaccinemanagement', '0012_auto_20230502_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vaccineappointmentdetails',
            name='address',
        ),
        migrations.RemoveField(
            model_name='vaccineappointmentdetails',
            name='mobile',
        ),
    ]