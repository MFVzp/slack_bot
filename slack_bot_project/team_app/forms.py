# -*- coding: utf-8 -*-
from django import forms


class ChannelForm(forms.Form):
    message_chanel_name = forms.CharField(label='Канал установки бота', max_length=100, strip=True)
