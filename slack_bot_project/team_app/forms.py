# -*- coding: utf-8 -*-
from django import forms
from .models import Team


class ChannelForm(forms.Form):
    message_chanel_name = forms.CharField(label='Канал установки бота', max_length=100, strip=True)


class AddModeratorForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.team_id = kwargs.pop('team_id', list())
        super(AddModeratorForm, self).__init__(*args, **kwargs)
        choices = list()
        if kwargs.get('data'):
            for choice in dict(kwargs.get('data')).get('moderators'):
                choices.append((choice, ''))
        else:
            for user in Team.objects.get(id=self.team_id).users.all():
                choices.append(
                    (user.id, user.get_full_name)
                )
        self.fields['moderators'] = forms.MultipleChoiceField(
            label='Пользователи',
            choices=choices
        )


class ChangeAdminForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.team_id = kwargs.pop('team_id', list())
        super(ChangeAdminForm, self).__init__(*args, **kwargs)
        choices = list()
        if kwargs.get('data'):
            for choice in dict(kwargs.get('data')).get('admin'):
                choices.append((choice, ''))
        else:
            for user in Team.objects.get(id=self.team_id).moderators.all():
                choices.append(
                    (user.id, user.get_full_name)
                )
        self.fields['admin'] = forms.ChoiceField(
            label='Модераторы',
            choices=choices
        )
