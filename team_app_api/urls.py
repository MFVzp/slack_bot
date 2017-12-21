from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'ask_messages/$', AskMessageListView.as_view(), name='ask_message_list'),
    url(r'ask_messages/(?P<pk>[0-9]+)/$', AskMessageDetailView.as_view(), name='ask_message_details'),
    url(r'teams/(?P<pk>[0-9]+)/$', TeamDetailUpdateView.as_view(), name='team_details'),
    url(r'teams/$', TeamListView.as_view(), name='team_list'),
    url(r'login_or_add_bot/$', LoginOrAddBotView.as_view(), name='login_or_add_bot'),
    url(r'register/$', RegisterView.as_view(), name='slack_register'),
    url(r'logout/$', LogoutView.as_view(), name='logout'),
]


