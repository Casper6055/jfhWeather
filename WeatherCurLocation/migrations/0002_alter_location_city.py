# Generated by Django 4.0.6 on 2022-08-01 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WeatherCurLocation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='city',
            field=models.CharField(max_length=255, verbose_name='Name of city'),
        ),
    ]
