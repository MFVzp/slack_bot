from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import *
from .forms import *


class TeamViewTest(TestCase):

    def setUp(self):
        self.users = list()
        self.number_of_users = 3
        for i in range(self.number_of_users):
            username = 'user' + str(i)
            first_name = username + '_first'
            last_name = username + '_last'
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password('qazwsx')
            user.save()
            self.users.append(user)
        self.teams = list()
        for i in range(self.number_of_users+1):
            team_name = 'team_name' + str(i)
            team_id = str(i)
            message_chanel_name = 'message_chanel_name' + str(i)
            team = Team.objects.create(
                team_name=team_name,
                team_id=team_id,
                message_chanel_name=message_chanel_name
            )
            self.teams.append(team)
        self.clients = list()
        for i in range(self.number_of_users):
            client = Client()
            client.login(
                username=self.users[i],
                password='qazwsx'
            )
            self.clients.append(client)
        self.teams[0].users.add(self.users[0])
        self.teams[1].moderators.add(self.users[0])
        self.teams[2].admin = self.users[0]
        self.teams[2].save()
        for i in range(len(self.teams)):
            for j in range(3):
                AskMessage.objects.create(
                    author_name=self.users[(i+j) % 3].first_name,
                    author_id=self.users[(i+j) % 3].username,
                    ts=str(i)+str(j),
                    channel='qwerty',
                    text='some text',
                    team=self.teams[i]
                )

    def test_team_list(self):
        client = self.clients[0]
        excluded_team = self.teams[2]
        response = client.get(reverse('slack:teams:team_list'))
        self.assertEqual(list(response.context.get('teams')), list(Team.objects.exclude(team_id=excluded_team.id)))

    def test_forms(self):
        user = self.users[0]
        client = self.clients[0]
        admin_team = user.admin_of_teams.all()[0]
        moderator_team = user.moderator_of_teams.all()[0]
        user_team = user.member_of_teams.all()[0]

        # Admin team ------------------
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': admin_team.id}))
        self.assertEqual(
            response.context.get('channel_form').as_p(),
            ChannelForm(initial={
                'message_chanel_name': admin_team.message_chanel_name
            }).as_p()
        )
        # without moderators
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': admin_team.id}))
        self.assertEqual(
            response.context.get('change_admin_form'),
            None
        )
        # with moderators
        admin_team.moderators.add(self.users[1])
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': admin_team.id}))
        self.assertEqual(
            response.context.get('change_admin_form').as_p(),
            ChangeAdminForm(team_id=admin_team.id).as_p()
        )
        # without users
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': admin_team.id}))
        self.assertEqual(
            response.context.get('moderators_add_form'),
            None
        )
        # with users
        admin_team.users.add(self.users[2])
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': admin_team.id}))
        self.assertEqual(
            response.context.get('moderators_add_form').as_p(),
            AddModeratorForm(team_id=admin_team.id).as_p()
        )

        # Moderator team --------------
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': moderator_team.id}))
        self.assertEqual(
            response.context.get('channel_form'),
            None
        )
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': moderator_team.id}))
        self.assertEqual(
            response.context.get('change_admin_form'),
            None
        )
        # without users
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': moderator_team.id}))
        self.assertEqual(
            response.context.get('moderators_add_form'),
            None
        )
        # with users
        moderator_team.users.add(self.users[2])
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': moderator_team.id}))
        self.assertEqual(
            response.context.get('moderators_add_form'),
            None
        )

        # User team --------------
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': user_team.id}))
        self.assertEqual(
            response.context.get('channel_form'),
            None
        )
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': user_team.id}))
        self.assertEqual(
            response.context.get('moderators_add_form'),
            None
        )
        # without moderators
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': user_team.id}))
        self.assertEqual(
            response.context.get('change_admin_form'),
            None
        )
        # with moderators
        user_team.moderators.add(self.users[1])
        response = client.get(reverse('slack:teams:team_details', kwargs={'pk': user_team.id}))
        self.assertEqual(
            response.context.get('change_admin_form'),
            None
        )
