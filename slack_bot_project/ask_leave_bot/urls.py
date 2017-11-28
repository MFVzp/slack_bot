from django.conf.urls import url
from .views import slack_oauth_view


urlpatterns = [
    url(r'^oauth/$', slack_oauth_view),
]
