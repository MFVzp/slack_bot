# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import User

from team_app.models import Team


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class TeamListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='slack:teams_api:team_details')

    class Meta:
        model = Team
        fields = ('team_name', 'url')


class TeamDetailSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    moderators = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ('team_name', 'message_chanel_name', 'users', 'moderators', 'admin')
