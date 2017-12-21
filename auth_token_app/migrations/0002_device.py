# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-21 10:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_token_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_agent', models.CharField(max_length=128)),
                ('ip_address', models.GenericIPAddressField()),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth_token_app.ManyDevicesExpiratoryToken')),
            ],
        ),
    ]
