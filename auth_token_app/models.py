import datetime

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication


def get_now_plus_1_day():
    return timezone.now() + datetime.timedelta(days=1)


class ManyDevicesExpiratoryToken(Token):
    expiration_date = models.DateTimeField(default=get_now_plus_1_day)


class Device(models.Model):
    user_agent = models.CharField(max_length=128, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    token = models.ForeignKey(ManyDevicesExpiratoryToken, on_delete=models.CASCADE, related_name='devices')


class MyTokenAuthentication(TokenAuthentication):

    model = ManyDevicesExpiratoryToken
