from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'(?P<pk>[0-9]+)/$', TeamDetailView.as_view(), name='team_details'),
    # url(r'(?P<pk>[0-9]+)/change_channel/$', ChangeChannelView.as_view(), name='change_channel'),
    # url(r'(?P<pk>[0-9]+)/change_admin/$', ChangeAdminView.as_view(), name='change_admin'),
    # url(r'(?P<pk>[0-9]+)/add_moderator/$', AddModeratorView.as_view(), name='add_moderator'),
    # url(r'(?P<pk>[0-9]+)/remove_moderator/$', RemoveModeratorView.as_view(), name='remove_moderator'),
    url(r'$', TeamListView.as_view(), name='team_list'),
]


