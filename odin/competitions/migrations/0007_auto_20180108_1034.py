# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-01-08 10:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0017_auto_20171121_1059'),
        ('applications', '0007_remove_applicationinfo_competition'),
        ('competitions', '0006_auto_20180108_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='application_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competition', to='applications.ApplicationInfo'),
        ),
        migrations.AddField(
            model_name='competition',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competitions', to='education.Course'),
        ),
    ]
