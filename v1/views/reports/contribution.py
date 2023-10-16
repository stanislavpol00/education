from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Example, Tip

from ...permissions import IsAuthenticated
from ..mixins import ContributionMixin


class ContributionView(ContributionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_id = request.user.id
        days = int(request.GET.get("days", 91))

        tips = Tip.objects.contributions(days=days, user_id=user_id)
        examples = Example.objects.contributions(days=days, user_id=user_id)

        data = self.serialize_data(tips, examples)

        data = data.get(user_id, [])

        return Response(data)
