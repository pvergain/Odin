# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-22 07:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20170607_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
