# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-23 11:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irodsapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image_columns',
            field=models.IntegerField(default=3),
        ),
    ]
