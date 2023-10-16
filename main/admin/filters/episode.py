from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from main.models import Episode
from libs.filters import Select2Filter


class EpisodeSelect2Filter(Select2Filter):
    title = _("Episode")
    parameter_name = "episode"
    ajax_url = reverse_lazy("autocomplete:episode")
    choices_queryset = Episode.objects.all()
