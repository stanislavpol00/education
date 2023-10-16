from taggit.models import Tag

from libs.autocomplete.views import BaseModelAutocompleteView


class TagAutocompleteView(BaseModelAutocompleteView):
    model = Tag
    search_fields = ["name", "slug"]
