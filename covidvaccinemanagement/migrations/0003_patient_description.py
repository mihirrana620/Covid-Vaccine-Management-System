# Generated by Django 3.1.3 on 2023-04-26 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covidvaccinemanagement', '0002_auto_20230426_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='description',
            field=models.TextField(default=0, max_length=500),
            preserve_default=False,
        ),
    ]
