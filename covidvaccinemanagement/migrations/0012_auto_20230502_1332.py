# Generated by Django 3.1.3 on 2023-05-02 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covidvaccinemanagement', '0011_vaccineappointmentdetails_patientid'),
    ]

    operations = [
        migrations.AddField(
            model_name='vaccineappointmentdetails',
            name='address',
            field=models.CharField(default=0, max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vaccineappointmentdetails',
            name='mobile',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
    ]