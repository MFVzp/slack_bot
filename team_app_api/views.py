from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from team_app.models import Team, AskMessage
from team_app_api import serializers


class TeamListView(generics.ListAPIView):
    serializer_class = serializers.TeamListSerializer

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        ).distinct()
        return queryset


class TeamDetailUpdateView(generics.RetrieveUpdateAPIView):

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        ).distinct()
        return queryset

    def get_object(self):
        self.object = super(TeamDetailUpdateView, self).get_object()
        return self.object

    def get_serializer_class(self, method='GET'):
        if self.request.user == self.object.admin:
            return serializers.TeamAdminDetailSerializer
        else:
            return serializers.TeamDetailSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = serializers.TeamUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        user = self.request.user
        team = self.get_object()
        if user == team.admin:
            super(TeamDetailUpdateView, self).partial_update(request, *args, **kwargs)
        else:
            return Response(
                data={
                    'error': 'You are not an admin in this team.',
                },
                status=status.HTTP_403_FORBIDDEN
            )


class TeamUpdateView(generics.UpdateAPIView):

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        ).distinct()
        return queryset

    def partial_update(self, request, *args, **kwargs):
        user = self.request.user
        team = self.get_object()
        if user == team.admin:
            super(TeamUpdateView, self).partial_update(request, *args, **kwargs)
        else:
            return Response(
                data={
                    'error': 'You are not an admin in this team.',
                },
                status=status.HTTP_403_FORBIDDEN
            )


class AskMessageListView(generics.ListAPIView):
    serializer_class = serializers.AskMessageListSerializer

    def get_queryset(self):
        queryset = AskMessage.objects.filter(
            author_id=self.request.user.username
        ).prefetch_related('answer_messages')
        return queryset


class AskMessageDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.AskMessageDetailSerializer

    def get_object(self):
        self.object = super(AskMessageDetailView, self).get_object()
        return self.object

    def get_queryset(self):
        queryset = AskMessage.objects.all().prefetch_related('answer_messages')
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        team = instance.team
        if self.request.user.username == instance.author_id or self.request.user == team.admin or self.request.user in team.moderators.all():
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response(
                data={
                    'error': 'It is not yours message and you are not an admin or moderator in this team.',
                },
                status=status.HTTP_403_FORBIDDEN
            )
