# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 11:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ask_leave_bot', '0002_team_message_chanel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='message_chanel',
            new_name='message_chanel_id',
        ),
        migrations.AddField(
            model_name='team',
            name='message_chanel_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]