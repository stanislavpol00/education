from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from main.models import Student
from libs.filters import Select2Filter


class StudentSelect2Filter(Select2Filter):
    title = _("Student")
    parameter_name = "student"
    ajax_url = reverse_lazy("autocomplete:student")
    choices_queryset = Student.objects.all()
