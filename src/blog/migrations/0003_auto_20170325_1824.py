# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-26 01:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20170325_1813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='album',
            old_name='cover_photo',
            new_name='cover_photo_url',
        ),
        migrations.AlterField(
            model_name='album',
            name='draft',
            field=models.BooleanField(default=True),
        ),
    ]
