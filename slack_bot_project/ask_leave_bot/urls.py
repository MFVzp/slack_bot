from django.conf.urls import url
from .views import slack_oauth_view, take_ask_message


urlpatterns = [
    url(r'^oauth/$', slack_oauth_view),
    url(r'^message/$', take_ask_message),
]
