from django.db import models


class Team(models.Model):
    team_name = models.CharField(max_length=200)
    team_id = models.CharField(max_length=20)
    bot_user_id = models.CharField(max_length=20)
    bot_access_token = models.CharField(max_length=100)

    def __str__(self):
        return self.team_name
