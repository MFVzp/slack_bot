from django.utils import timezone

from slack_bot_project.celery import app
from .models import ManyDevicesExpiratoryToken


@app.task
def clean_expired_tokens():
    expired_tokens = ManyDevicesExpiratoryToken.objects.filter(expiration_date__lte=timezone.now()).delete()
    return '{}: {} expired tokens deleted.'.format(timezone.now(), expired_tokens[0])

