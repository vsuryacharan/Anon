# Generated by Django 5.1.1 on 2024-10-06 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdfdocument',
            name='audio_file',
            field=models.FileField(blank=True, null=True, upload_to='audio/'),
        ),
    ]