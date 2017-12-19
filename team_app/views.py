from django.views import generic
from django.urls import reverse_lazy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db import transaction

from .models import Team
from team_app import forms as team_form


class TeamListView(LoginRequiredMixin, generic.ListView):
    login_url = reverse_lazy('index')
    model = Team
    template_name = 'team_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        queryset = Team.objects.filter(
            Q(users=self.request.user) |
            Q(moderators=self.request.user) |
            Q(admin=self.request.user)
        )
        return queryset


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('index')
    model = Team
    template_name = 'team_details.html'
    context_object_name = 'team'

    def get_queryset(self):
        queryset = Team.objects.select_related('admin').prefetch_related('users', 'moderators', 'ask_messages')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        team = self.get_object()
        message_chanel_name = team.message_chanel_name
        if self.request.user == team.admin:
            context['channel_form'] = team_form.ChannelForm(
                initial={
                    'message_chanel_name': message_chanel_name
                }
            )
            if team.users.all().exists() and self.request.user == team.admin:
                context['moderators_add_form'] = team_form.AddModeratorForm(
                    team_id=team.id
                )
            if team.moderators.all().exists() and self.request.user == team.admin:
                context['change_admin_form'] = team_form.ChangeAdminForm(
                    team_id=team.id
                )
        return context


class ChangeChannelView(LoginRequiredMixin, generic.FormView):
    login_url = reverse_lazy('index')
    form_class = team_form.ChannelForm

    def form_valid(self, form):
        message_chanel_name = form.cleaned_data.get('message_chanel_name')
        Team.objects.filter(id=self.kwargs.get('pk')).update(message_chanel_name=message_chanel_name)
        return super(ChangeChannelView, self).form_valid(form)

    def get_success_url(self):
        return reverse('slack:teams:team_details', kwargs={'pk': self.kwargs.get('pk')})


class ChangeAdminView(LoginRequiredMixin, generic.FormView):
    login_url = reverse_lazy('index')
    form_class = team_form.ChangeAdminForm

    def form_valid(self, form):
        admin_id = form.cleaned_data.get('admin')
        team = Team.objects.get(id=self.kwargs.get('pk'))
        new_admin = User.objects.get(id=admin_id)
        with transaction.atomic():
            team.moderators.add(self.request.user)
            team.admin = new_admin
            team.save()
        return super(ChangeAdminView, self).form_valid(form)

    def get_success_url(self):
        return reverse('slack:teams:team_details', kwargs={'pk': self.kwargs.get('pk')})


class AddModeratorView(LoginRequiredMixin, generic.FormView):
    login_url = reverse_lazy('index')
    form_class = team_form.AddModeratorForm

    def form_valid(self, form):
        moderators_id = form.cleaned_data.get('moderators')
        team = Team.objects.get(id=self.kwargs.get('pk'))
        for moderator_id in moderators_id:
            user = User.objects.get(id=moderator_id)
            with transaction.atomic():
                team.users.remove(user)
                team.moderators.add(user)
        return super(AddModeratorView, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)

    def get_success_url(self):
        return reverse('slack:teams:team_details', kwargs={'pk': self.kwargs.get('pk')})


class RemoveModeratorView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        moderator_id = request.POST.get('moderator_id')
        if moderator_id:
            team = Team.objects.get(id=kwargs.get('pk'))
            user = User.objects.get(id=moderator_id)
            with transaction.atomic():
                team.moderators.remove(user)
                team.users.add(user)
        return HttpResponseRedirect(reverse('slack:teams:team_details', kwargs={'pk': kwargs.get('pk')}))
