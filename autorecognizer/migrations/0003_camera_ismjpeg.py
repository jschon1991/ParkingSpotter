# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-18 19:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autorecognizer', '0002_camera_isstream'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='isMjpeg',
            field=models.BooleanField(default=False, verbose_name='Is stream url for this camera in mjpg format.'),
        ),
    ]
