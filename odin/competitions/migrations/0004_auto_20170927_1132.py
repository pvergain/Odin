# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-27 11:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0003_competitiontest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionmaterial',
            name='identifier',
            field=models.CharField(max_length=255),
        ),
    ]