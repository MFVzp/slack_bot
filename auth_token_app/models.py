import datetime

from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication


def get_now_plus_1_day():
    return datetime.datetime.now() + datetime.timedelta(days=1)


class ManyDevicesExpiratoryToken(Token):
    used_devices = models.PositiveSmallIntegerField(default=0)
    expiration_date = models.DateTimeField(default=get_now_plus_1_day)


class MyTokenAuthentication(TokenAuthentication):

    model = ManyDevicesExpiratoryToken
