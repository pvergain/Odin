# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-28 12:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationSolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, null=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='applications.Application')),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('gradable', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IncludedApplicationTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('gradable', models.BooleanField(default=False)),
                ('application_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='applications.ApplicationInfo')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='included_tasks', to='applications.ApplicationTask')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='applicationsolution',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='applications.IncludedApplicationTask'),
        ),
    ]
