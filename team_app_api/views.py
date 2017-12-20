from rest_framework import generics
from django.db.models import Q

from team_app.models import Team
from team_app_api import serializers


class TeamListView(generics.ListAPIView):
    serializer_class = serializers.TeamListSerializer

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        ).distinct()
        print(queryset.query)
        return queryset


class TeamDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.TeamDetailSerializer

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        ).distinct().select_related('admin').prefetch_related('users', 'moderators', 'ask_messages')
        return queryset
