from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'ask_messages/$', AskMessageListView.as_view(), name='ask_message_list'),
    url(r'ask_messages/(?P<pk>[0-9]+)/$', AskMessageDetailView.as_view(), name='ask_message_details'),
    # url(r'(?P<pk>[0-9]+)/change_channel/$', ChangeChannelView.as_view(), name='change_channel'),
    # url(r'(?P<pk>[0-9]+)/change_admin/$', ChangeAdminView.as_view(), name='change_admin'),
    # url(r'(?P<pk>[0-9]+)/add_moderator/$', AddModeratorView.as_view(), name='add_moderator'),
    # url(r'(?P<pk>[0-9]+)/remove_moderator/$', RemoveModeratorView.as_view(), name='remove_moderator'),
    url(r'(?P<pk>[0-9]+)/$', TeamDetailUpdateView.as_view(), name='team_details'),
    url(r'$', TeamListView.as_view(), name='team_list'),
]


