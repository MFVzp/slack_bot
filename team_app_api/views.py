from rest_framework import generics
from django.db.models import Q

from team_app.models import Team
from .serializers import TeamSerializer


class TeamListView(generics.ListAPIView):
    serializer_class = TeamSerializer

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        )
        return queryset


class TeamDetailView(generics.RetrieveAPIView):
    serializer_class = TeamSerializer

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        ).select_related('admin').prefetch_related('users', 'moderators', 'ask_messages')
        return queryset
