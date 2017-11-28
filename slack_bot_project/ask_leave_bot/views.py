from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import requests
import json

from .models import Team


def index(request):
    client_id = settings.SLACK_CLIENT_ID
    return render(request, 'index.html', {'client_id': client_id})


def slack_oauth_view(request):
    code = request.GET['code']

    params = {
        'code': code,
        'client_id': settings.SLACK_CLIENT_ID,
        'client_secret': settings.SLACK_CLIENT_SECRET
    }
    url = 'https://slack.com/api/oauth.access'
    json_response = requests.get(url, params)
    data = json.loads(json_response.text)
    Team.objects.get_or_create(
        team_name=data['team_name'],
        team_id=data['team_id'],
        bot_user_id=data['bot']['bot_user_id'],
        bot_access_token=data['bot']['bot_access_token']
    )
    return HttpResponse('Bot added to your Slack team!')


@csrf_exempt
@require_POST
def take_ask_message(request):
    print(request.POST)
    return HttpResponse('Your asking was received.')
