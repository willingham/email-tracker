# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-14 17:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_auto_20170914_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='send_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]