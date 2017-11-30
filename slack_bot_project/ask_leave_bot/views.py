# -*- coding: utf-8 -*-
import os
import json

from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from slackclient import SlackClient
import requests

from .models import Team, AskMessage, AnswerMessage


def index(request):
    client_id = os.environ.get("SLACK_CLIENT_ID")
    return render(request, 'index.html', {'client_id': client_id})


def slack_oauth_view(request):
    code = request.GET['code']

    params = {
        'code': code,
        'client_id': os.environ.get("SLACK_CLIENT_ID"),
        'client_secret': os.environ.get("SLACK_CLIENT_SECRET"),
    }
    url = 'https://slack.com/api/oauth.access'
    json_response = requests.get(url, params)
    data = json.loads(json_response.text)
    Team.objects.get_or_create(
        team_name=data['team_name'],
        team_id=data['team_id'],
        bot_user_id=data['bot']['bot_user_id'],
    )
    return HttpResponse('Bot added to your Slack team!')


@csrf_exempt
@require_POST
def take_ask_message(request):
    if request.POST.get('token') == os.environ.get("VERIFICATION_TOKEN"):
        data = request.POST
        team = Team.objects.get(team_id=data.get('team_id'))
        slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        all_channels = slack_client.api_call(
            'groups.list'
        )
        message_channels = [channel for channel in all_channels['groups'] if channel['name'] == team.message_chanel_name]
        message_channel = message_channels and message_channels[0]
        if message_channel or True:
            ask_message = '_Пользователю <@{0}> нужно отлучиться_ `"{1}"`'.format(
                data.get('user_id'),
                data.get('text')
            )
            resp = slack_client.api_call(
                'chat.postMessage',
                channel='ask_bot_test_by_tia',
                text=ask_message,
                as_user=True,
                link_names=True,
            )
            AskMessage.objects.create(
                author_name=data.get('user_name'),
                author_id=data.get('user_id'),
                ts=resp['ts'],
                channel=resp['channel'],
                text=data.get('text'),
                team=team
            )
        return HttpResponse('Your asking was received.')
    else:
        raise PermissionDenied


@csrf_exempt
@require_POST
def take_event(request):
    data = json.loads(request.body.decode())
    if data.get('token') == os.environ.get("VERIFICATION_TOKEN"):
        if data.get('challenge'):
            return HttpResponse(data.get('challenge'))
        elif data.get('event').get('thread_ts'):
            try:
                event = data.get('event')
                ask_message = AskMessage.objects.get(ts=event.get('thread_ts'))
                AnswerMessage.objects.create(
                    author_id=event.get('user'),
                    ts=event.get('ts'),
                    text=event.get('text'),
                    ask_message=ask_message
                )
                slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
                resp = slack_client.api_call(
                    'conversations.open',
                    users=ask_message.author_id
                )
                if resp['ok']:
                    print(event)
                    answer = '_На Ваш запрос(`{0}`) <@{1}> ответил_ "`{2}`"'.format(
                        ask_message.text,
                        event.get('user'),
                        event.get('text')
                    )
                    slack_client.api_call(
                        'chat.postMessage',
                        channel=resp['channel']['id'],
                        text=answer,
                        as_user=True,
                        link_names=True,
                    )
                ask_message.is_answered = True
            except:
                pass
        return HttpResponse()
    raise PermissionDenied
