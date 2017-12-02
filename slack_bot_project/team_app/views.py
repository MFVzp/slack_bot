from django.views import generic

from .models import Team


class TeamListView(generic.ListView):
    model = Team
    template_name = 'team_list.html'
    context_object_name = 'teams'
