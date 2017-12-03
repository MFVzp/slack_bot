from django.test import TestCase
from django.contrib.auth.models import User

from .models import *


class TeamDetailViewTest(TestCase):

    def SetUp(self):
        self.users = list()
        for i in range(3):
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
        for i in range(3):
            team_name = 'team_name' + str(i)
            team_id = str(i)
            message_chanel_name = 'message_chanel_name' + str(i)
            team = Team.objects.create(
                team_name=team_name,
                team_id=team_id,
                message_chanel_name=message_chanel_name
            )
            for user in self.users:
                team.users.add(user)
            team.moderators.add(self.users[i])
            team.moderators.add(self.users[(i+1) % 3])
            team.admin = self.users[i]
            team.save()
            self.teams.append(team)

    def 
