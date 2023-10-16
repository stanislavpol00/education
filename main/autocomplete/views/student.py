from main.models import Student
from libs.autocomplete.views import BaseModelAutocompleteView


class StudentAutocompleteView(BaseModelAutocompleteView):
    model = Student
    search_fields = ["nickname", "first_name", "last_name"]
