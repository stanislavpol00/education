from main.models import Episode
from libs.autocomplete.views import BaseModelAutocompleteView


class EpisodeAutocompleteView(BaseModelAutocompleteView):
    model = Episode
    search_fields = ["title"]
