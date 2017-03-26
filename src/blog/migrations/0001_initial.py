# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-26 01:12
from __future__ import unicode_literals

import blog.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('cover_photo', models.URLField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('slug', models.SlugField()),
                ('draft', models.BooleanField(default=False)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('editor', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_time', '-updated_time'],
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('image_name', models.CharField(max_length=128)),
                ('image_path', models.CharField(max_length=256)),
                ('image', models.ImageField(blank=True, null=True, upload_to=blog.models.upload_location_photo, verbose_name='Photo')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('width', models.IntegerField(blank=True, default=0, null=True)),
                ('height', models.IntegerField(blank=True, default=0, null=True)),
                ('size', models.BigIntegerField(blank=True, default=0, null=True)),
                ('description', models.TextField(blank=True)),
                ('device_make', models.CharField(blank=True, max_length=128, null=True)),
                ('device_model', models.CharField(blank=True, max_length=128, null=True)),
                ('orientation', models.CharField(blank=True, max_length=2, null=True)),
                ('taken_time', models.DateTimeField(blank=True, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=8, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('address', models.CharField(blank=True, max_length=256, null=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Album', verbose_name='album')),
                ('author', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('editor', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['image_name', 'created_time', 'updated_time'],
            },
        ),
    ]
