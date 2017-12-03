# -*- coding: utf-8 -*-
from django import forms


class ChannelForm(forms.Form):
    message_chanel_name = forms.CharField(label='Канал установки бота', max_length=100, strip=True)


class AddModeratorForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', list())
        super(AddModeratorForm, self).__init__(*args, **kwargs)
        choices = list()
        if kwargs.get('data'):
            for choice in kwargs.get('data').get('moderators'):
                choices.append((choice, ''))
        else:
            for user in self.queryset:
                choices.append(
                    (user.id, user.get_full_name)
                )
        self.fields['moderators'] = forms.MultipleChoiceField(
            label='Пользователи',
            choices=choices
        )


class ChangeAdminForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', list())
        super(ChangeAdminForm, self).__init__(*args, **kwargs)
        choices = list()
        if kwargs.get('data'):
            for choice in kwargs.get('data').get('admin'):
                choices.append((choice, ''))
        else:
            for user in self.queryset:
                choices.append(
                    (user.id, user.get_full_name)
                )
        self.fields['admin'] = forms.ChoiceField(
            label='Модераторы',
            choices=choices
        )
