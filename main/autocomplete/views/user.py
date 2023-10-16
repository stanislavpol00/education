from django.contrib.auth import get_user_model

from libs.autocomplete.views import BaseModelAutocompleteView

User = get_user_model()


class UserAutocompleteView(BaseModelAutocompleteView):
    model = User
    search_fields = ["username", "email", "first_name", "last_name"]
