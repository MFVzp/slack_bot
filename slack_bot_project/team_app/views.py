from django.views import generic
from django.shortcuts import get_list_or_404
from django.core.urlresolvers import reverse

from .models import Team
from .forms import ChannelForm


class TeamListView(generic.ListView):
    model = Team
    template_name = 'team_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        queryset = get_list_or_404(Team, users=self.request.user)
        return queryset


class TeamDetailView(generic.DetailView):
    model = Team
    template_name = 'team_details.html'
    context_object_name = 'team'

    def get_queryset(self):
        queryset = Team.objects.select_related('admin').prefetch_related('users', 'moderators', 'ask_messages')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        message_chanel_name = self.get_object().message_chanel_name
        context['form'] = ChannelForm(
            initial={
                'message_chanel_name': message_chanel_name
            }
        )
        return context


class ChangeChannelView(generic.FormView):
    form_class = ChannelForm

    def form_valid(self, form):
        message_chanel_name = form.cleaned_data.get('message_chanel_name')
        team = Team.objects.get(id=self.kwargs.get('pk'))
        team.message_chanel_name = message_chanel_name
        team.save()
        return super(ChangeChannelView, self).form_valid(form)

    def get_success_url(self):
        return reverse('slack:teams:team_details', kwargs={'pk': self.kwargs.get('pk')})
