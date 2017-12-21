from django.conf.urls import url, include
from .views import slack_oauth_view, take_ask_message_view, take_event_view, logout_view


urlpatterns = [
    url(r'api/', include('team_app_api.urls', namespace='teams_api')),
    url(r'teams/', include('team_app.urls', namespace='teams')),
    url(r'oauth/register/$', slack_oauth_view),
    url(r'message/$', take_ask_message_view),
    url(r'events/$', take_event_view),
    url(r'logout/$', logout_view, name='logout'),
]
