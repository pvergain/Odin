# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-23 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0014_remove_course_is_competition'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='attendable',
            field=models.BooleanField(default=True),
        ),
    ]
