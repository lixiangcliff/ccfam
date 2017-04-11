# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-11 03:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_auto_20170410_2047'),
        ('albums', '0002_auto_20170410_2047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='cover_photo_url',
        ),
        migrations.AddField(
            model_name='album',
            name='cover_photo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='photos.Photo', verbose_name='cover_photo'),
        ),
    ]
