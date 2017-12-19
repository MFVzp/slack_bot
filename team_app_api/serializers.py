# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import User

from team_app.models import Team


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class TeamSerializer(serializers.ModelSerializer):
    # users = UserSerializer(many=True, read_only=True)
    # moderators = UserSerializer(many=True, read_only=True)
    # admin = UserSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ('team_name', 'team_id', 'message_chanel_name', 'users', 'moderators', 'admin')
