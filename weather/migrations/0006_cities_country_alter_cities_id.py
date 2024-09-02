# Generated by Django 5.0.6 on 2024-06-06 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0005_alter_myuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='cities',
            name='country',
            field=models.CharField(default=None, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cities',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
