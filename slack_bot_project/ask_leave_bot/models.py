from django.db import models


class Team(models.Model):
    team_name = models.CharField(max_length=200)
    team_id = models.CharField(max_length=20)
    bot_user_id = models.CharField(max_length=20)
    bot_access_token = models.CharField(max_length=100)
    message_chanel_id = models.CharField(max_length=100, blank=True, null=True)
    message_chanel_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.team_name


class AskMessage(models.Model):
    author_name = models.CharField(max_length=200)
    author_id = models.CharField(max_length=20)
    ts = models.CharField(max_length=40)
    channel = models.CharField(max_length=20)
    text = models.TextField()
    create_date = models.DateField(auto_now=False, auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='ask_messages')

    def __str__(self):
        return self.text[:10]


class AnswerMessage(models.Model):
    author_id = models.CharField(max_length=20)
    ts = models.CharField(max_length=40)
    text = models.TextField()
    create_date = models.DateField(auto_now=False, auto_now_add=True)
    ask_message = models.ForeignKey(AskMessage, on_delete=models.CASCADE, related_name='answer_messages')
