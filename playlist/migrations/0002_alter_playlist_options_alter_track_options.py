# Generated by Django 4.0.6 on 2022-09-02 13:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='playlist',
            options={'verbose_name': 'Playlist', 'verbose_name_plural': 'Playlists'},
        ),
        migrations.AlterModelOptions(
            name='track',
            options={'verbose_name': 'Track', 'verbose_name_plural': 'Tracks'},
        ),
    ]
