# -*- coding: utf-8 -*-
import json

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from slackclient import SlackClient
import requests

from team_app.models import Team, AskMessage, AnswerMessage
from slack_bot_project import settings


def index_view(request):
    client_id = settings.SLACK_CLIENT_ID
    return render(request, 'index.html', {'client_id': client_id})


def slack_oauth_view(request):
    code = request.GET['code']

    params = {
        'code': code,
        'client_id': settings.SLACK_CLIENT_ID,
        'client_secret': settings.SLACK_CLIENT_SECRET,
    }
    url = 'https://slack.com/api/oauth.access'
    json_response = requests.get(url, params)
    data = json.loads(json_response.text)

    team, team_created = Team.objects.get_or_create(
        team_name=data['team_name'],
        team_id=data['team_id']
    )
    password = data['user_id']*2
    if not request.user.is_authenticated:
        slack_client = SlackClient(data['access_token'])
        profile = slack_client.api_call('users.profile.get')['profile']
        user = authenticate(
            request=request,
            username=data['user_id'],
            password=password
        )
        if user is None:
            user = User.objects.create_user(
                username=data['user_id'],
                first_name=profile['first_name'],
                last_name=profile['last_name'],
                email=profile['email']
            )
            user.set_password(password)
            user.save()
            if not team_created:
                team.users.add(user)
        login(
            request=request,
            user=user
        )
    else:
        user = request.user
    if team_created:
        team.admin = user
        team.save()
    return redirect('index')


@csrf_exempt
@require_POST
def take_ask_message_view(request):
    if request.POST.get('token') == settings.VERIFICATION_TOKEN:
        data = request.POST
        team = Team.objects.get(team_id=data.get('team_id'))
        if team.message_chanel_name:
			slack_client = SlackClient(settings.SLACK_BOT_TOKEN)
            ask_message = '_Пользователю <@{0}> нужно отлучиться_ `"{1}"`'.format(
                data.get('user_id'),
                data.get('text')
            )
            resp = slack_client.api_call(
                'chat.postMessage',
                channel=team.message_chanel_name,
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
			return HttpResponse('Message channel have not set', status_code='405', reason_phrase='Method Not Allowed')
    else:
        return HttpResponse('', status_code='403', reason_phrase='Forbidden')


@csrf_exempt
@require_POST
def take_event_view(request):
    data = json.loads(request.body.decode())
    if data.get('token') == settings.VERIFICATION_TOKEN:
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
                slack_client = SlackClient(settings.SLACK_BOT_TOKEN)
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


@login_required(
    login_url='https://slack.com/oauth/authorize?scope=bot&client_id={0}'.format(
        settings.SLACK_CLIENT_ID
    )
)
def logout_view(request):
    logout(request)
    return redirect('index')
