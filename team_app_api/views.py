import datetime

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import requests
from slackclient import SlackClient


from team_app.models import Team, AskMessage
from team_app_api import serializers
from auth_token_app.models import ManyDevicesExpiratoryToken, Device


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


class LoginOrAddBotView(views.APIView):

    def get(self, request):
        scope = 'bot'
        return Response({
            'redirect_url': 'https://slack.com/oauth/authorize?scope={0}&client_id={1}'.format(
                scope,
                settings.SLACK_CLIENT_ID
            ),
        })


class RegisterView(views.APIView):

    def get(self, request):
        code = request.GET['code']

        params = {
            'code': code,
            'client_id': settings.SLACK_CLIENT_ID,
            'client_secret': settings.SLACK_CLIENT_SECRET,
        }
        url = 'https://slack.com/api/oauth.access'
        data = requests.get(url, params).json()

        if data.get('access_token') and not data.get('error'):
            response_context = dict()
            team, team_created = Team.objects.get_or_create(
                team_name=data['team_name'],
                team_id=data['team_id']
            )
            password = data['user_id'] * 2
            if not request.user.is_authenticated:
                slack_client = SlackClient(data['access_token'])
                profile = slack_client.api_call('users.profile.get')['profile']
                user = authenticate(
                    request=request,
                    username=data['user_id'],
                    password=password
                )
                if user is None:
                    user = User.objects.create_user(
                        username=data['user_id'],
                        first_name=profile['first_name'],
                        last_name=profile['last_name'],
                        email=profile['email']
                    )
                    user.set_password(password)
                    user.save()
                    if not team_created:
                        team.users.add(user)
                if user:
                    token, token_created = ManyDevicesExpiratoryToken.objects.get_or_create(
                        user=user
                    )
                    if not token_created:
                        if datetime.datetime.now() > token.expiration_date:
                            token.delete()
                            token = ManyDevicesExpiratoryToken.objects.create(
                                user=user
                            )
                    Device.objects.get_or_create(
                        user_agent=self.request.META.get('HTTP_USER_AGENT'),
                        ip_address=self.request.META.get('REMOTE_ADDR'),
                        token=token
                    )
                    response_context['access_token'] = 'Token {}'.format(user.auth_token.key)

            else:
                user = request.user
            if team_created:
                team.admin = user
                team.save()
                response_context['team_info'] = 'Team {} successfully added.'.format(team.team_name)
            return Response(data=response_context)
        else:
            return Response(
                data={
                    'error': 'Your authentication failed.',
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(views.APIView):

    def get(self, request):
        token = self.request.user.auth_token
        try:
            device = Device.objects.get(
                user_agent=self.request.META.get('HTTP_USER_AGENT'),
                ip_address=self.request.META.get('REMOTE_ADDR'),
                token=token
            )
        except ObjectDoesNotExist:
            return Response(
                data={
                    'error': 'You are not authorize from this device(User agent: {}; IP address: {}).'.format(
                        self.request.META.get('HTTP_USER_AGENT'),
                        self.request.META.get('REMOTE_ADDR')
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        device.delete()
        if not token.devices.all().exists():
            token.delete()
