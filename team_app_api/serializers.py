# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import User

from team_app.models import Team, AskMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class AskMessageListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='slack:teams_api:ask_message_details')

    class Meta:
        model = AskMessage
        fields = ('author_name', 'url')


class AskMessageDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = AskMessage
        fields = ('author_name', 'text', 'create_date', 'is_answered')


class AskMessageSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='slack:teams_api:ask_message_details'
    )

    class Meta:
        model = AskMessage
        fields = ('url', )


class TeamListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='slack:teams_api:team_details')

    class Meta:
        model = Team
        fields = ('team_name', 'url')


class TeamDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ('team_name', 'ask_messages')

    def __init__(self, *args, **kwargs):
        import pudb
        pudb.set_trace()
        context = kwargs.get('context')
        super(TeamDetailSerializer, self).__init__(*args, **kwargs)
        if context:
            user = context['request'].user
            team = context['view'].object
            if user in team.moderators.all():
                queryset = team.ask_messages.all()
            else:
                queryset = team.ask_messages.filter(author_id=user.username)
            self.fields['ask_messages'] = AskMessageSerializer(
                queryset,
                many=True
            )


class TeamAdminDetailSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    moderators = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)
    ask_messages = AskMessageSerializer(many=True)

    class Meta:
        model = Team
        fields = ('team_name', 'message_chanel_name', 'users', 'moderators', 'admin', 'ask_messages')


class TeamUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ('message_chanel_name', )
