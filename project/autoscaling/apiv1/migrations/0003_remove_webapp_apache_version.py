# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-11 10:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiv1', '0002_auto_20160311_1003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webapp',
            name='apache_version',
        ),
    ]
