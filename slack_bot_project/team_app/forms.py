# -*- coding: utf-8 -*-
from django import forms


class ChannelForm(forms.Form):
    message_chanel_name = forms.CharField(label='Канал установки бота', max_length=100, strip=True)


class AddModeratorForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        super(AddModeratorForm, self).__init__(*args, **kwargs)
        choices = list()
        for user in self.queryset:
            choices.append(
                (user.id, user.get_full_name)
            )
        self.fields['moderators'] = forms.MultipleChoiceField(
            label='Пользователи',
            choices=choices
        )
