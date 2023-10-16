from rest_framework.response import Response

from main.models import Example, Tip

from ..mixins import ContributionMixin
from .base import BaseManagerView


class ManagerContributionView(ContributionMixin, BaseManagerView):
    def get(self, request, format=None):
        params = self.get_params_filters(request)
        user_id = params.get("user")
        days = params.get("days", 91)

        tips = Tip.objects.contributions(days=days)
        examples = Example.objects.contributions(days=days)
        if user_id:
            user_id = int(user_id)
            tips = tips.filter(added_by=user_id)
            examples = examples.filter(added_by=user_id)

        data = self.serialize_data(tips, examples)
        if user_id:
            data = data.get(user_id, [])

        return Response(data)
