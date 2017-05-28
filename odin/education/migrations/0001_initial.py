# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-27 21:08
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=uuid.uuid4, max_length=110, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('repository', models.URLField(blank=True)),
                ('video_channel', models.URLField(blank=True)),
                ('facebook_group', models.URLField(blank=True)),
                ('generate_certificates_delta', models.DurationField(default=datetime.timedelta(15))),
            ],
        ),
        migrations.CreateModel(
            name='CourseAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_assignments', to='education.Course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verbose', models.TextField(blank=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='description', to='education.Course')),
            ],
        ),
        migrations.CreateModel(
            name='IncludedMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('url', models.URLField(blank=True)),
                ('content', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lectures', to='education.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('url', models.URLField(blank=True)),
                ('content', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('users.baseuser',),
        ),
        migrations.CreateModel(
            name='StudentNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.TextField(blank=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='education.CourseAssignment')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('users.baseuser',),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='education.Course')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('number', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.AddField(
            model_name='topic',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='education.Week'),
        ),
        migrations.AddField(
            model_name='studentnote',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='education.Teacher'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='present_students',
            field=models.ManyToManyField(related_name='lectures', to='education.Student'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='week',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lectures', to='education.Week'),
        ),
        migrations.AddField(
            model_name='includedmaterial',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='included_materials', to='education.Material'),
        ),
        migrations.AddField(
            model_name='includedmaterial',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='education.Topic'),
        ),
        migrations.AddField(
            model_name='courseassignment',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_assignments', to='education.Student'),
        ),
        migrations.AddField(
            model_name='courseassignment',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_assignments', to='education.Teacher'),
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(through='education.CourseAssignment', to='education.Student'),
        ),
        migrations.AddField(
            model_name='course',
            name='teachers',
            field=models.ManyToManyField(through='education.CourseAssignment', to='education.Teacher'),
        ),
        migrations.AddField(
            model_name='certificate',
            name='assignment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='education.CourseAssignment'),
        ),
        migrations.AlterUniqueTogether(
            name='courseassignment',
            unique_together=set([('teacher', 'course'), ('student', 'course')]),
        ),
    ]