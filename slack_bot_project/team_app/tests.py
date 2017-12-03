from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import *


class TeamViewTest(TestCase):

    def setUp(self):
        self.users = list()
        self.number_of_users = 4
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
        for i in range(self.number_of_users-1):
            team_name = 'team_name' + str(i)
            team_id = str(i)
            message_chanel_name = 'message_chanel_name' + str(i)
            team = Team.objects.create(
                team_name=team_name,
                team_id=team_id,
                message_chanel_name=message_chanel_name
            )
            team.users.add(self.users[(i+2) % self.number_of_users])
            team.moderators.add(self.users[(i+1) % self.number_of_users])
            team.admin = self.users[i]
            team.save()
            self.teams.append(team)
        self.clients = list()
        for i in range(self.number_of_users):
            client = Client()
            client.login(
                username=self.users[i],
                password='qazwsx'
            )
            self.clients.append(client)
        for i in range(len(self.teams)):
            for j in range(3):
                AskMessage.objects.create(
                    author_name=self.users[(i+j) % 4].first_name,
                    author_id=self.users[(i+j) % 4].username,
                    ts=str(i)+str(j),
                    channel='qwerty',
                    text='some text',
                    team=self.teams[i]
                )

    def test_team_list(self):
        response = self.clients[0].get(reverse('slack:teams:team_list'))
        self.assertEqual(response.context['teams'], list(Team.objects.exclude(team_id=1)))

    def test_messages(self):
        admin_team = self.users[0].admin_of_teams.all[0]
        moderator_team = self.users[0].moderator_of_teams.all().exclude(admin_team)[0]
        user_team = self.users[0].member_of_teams.all().exclude(admin_team)[0]
        print()
        response = self.clients[0].get(reverse('slack:teams:team_details', kwargs={'pk': team.id}))

