# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 20:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_photo_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='slug',
            field=models.SlugField(),
        ),
    ]