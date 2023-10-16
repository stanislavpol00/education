from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from taggit.models import Tag

from libs.filters import Select2Filter


class TagSelect2Filter(Select2Filter):
    title = _("Tag")
    parameter_name = "tags"
    ajax_url = reverse_lazy("autocomplete:tag")
    choices_queryset = Tag.objects.all()
    multiple = True
