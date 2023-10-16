from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from libs.filters import Select2Filter

User = get_user_model()


class UserSelect2Filter(Select2Filter):
    title = _("User")
    parameter_name = "user"
    ajax_url = reverse_lazy("autocomplete:user")
    choices_queryset = User.objects.all()
