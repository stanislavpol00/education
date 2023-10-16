from main.models import Tip
from libs.autocomplete.views import BaseModelAutocompleteView


class TipAutocompleteView(BaseModelAutocompleteView):
    model = Tip
    search_fields = ["title", "id"]
