# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-23 09:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Uploader',
            fields=[
                ('auto_increment_id', models.AutoField(primary_key=True, serialize=False)),
                ('original_filename', models.CharField(max_length=1024)),
                ('secret', models.BooleanField(default=False)),
                ('secret_key', models.CharField(max_length=1024, null=True)),
                ('file_ext', models.CharField(max_length=10)),
                ('delete_key', models.CharField(max_length=1024)),
                ('comment', models.CharField(max_length=1024, null=True)),
                ('upload_date', models.DateTimeField(auto_now=True)),
                ('size', models.IntegerField(null=True)),
                ('thumbnail', models.BooleanField(default=False)),
            ],
        ),
    ]
