# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-10 13:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0009_auto_20170710_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='education.IncludedTask'),
        ),
    ]
