from django.conf.urls import url
from .views import TeamListView, TeamDetailView, ChangeChannelView


urlpatterns = [
    url(r'(?P<pk>[0-9]+)/$', TeamDetailView.as_view(), name='team_details'),
    url(r'(?P<pk>[0-9]+)/change_channel/$', ChangeChannelView.as_view(), name='change_channel'),
    url(r'$', TeamListView.as_view(), name='team_list'),
]


