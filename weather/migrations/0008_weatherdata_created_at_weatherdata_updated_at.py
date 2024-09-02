# Generated by Django 5.0.6 on 2024-06-06 15:55

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0007_remove_myuser_cities_remove_weatherdata_weather_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherdata',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='weatherdata',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
