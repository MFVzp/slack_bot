# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import User

from team_app.models import Team, AskMessage


class TeamListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='slack:teams_api:team_details')

    class Meta:
        model = Team
        fields = ('team_name', 'url')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class AskMessageListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='slack:teams_api:ask_message_details')

    class Meta:
        model = AskMessage
        fields = ('author_name', 'url')


class AskMessageSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='slack:teams_api:ask_message_details')

    class Meta:
        model = AskMessage
        fields = ('url', )


class AskMessageDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = AskMessage
        fields = ('author_name', 'text', 'create_date', 'is_answered')


class TeamDetailSerializer(serializers.ModelSerializer):
    ask_messages = AskMessageSerializer(many=True)

    class Meta:
        model = Team
        fields = ('team_name', 'ask_messages')


class TeamAdminDetailSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    moderators = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)
    ask_messages = AskMessageSerializer(many=True)

    class Meta:
        model = Team
        fields = ('team_name', 'message_chanel_name', 'users', 'moderators', 'admin', 'ask_messages')
