from rest_framework.generics import ListAPIView

from main.models import Tip

from ...filters import RecentTipFilter
from ...pagination import StandardResultsSetPagination
from ...permissions import IsAuthenticated
from ...serializers import LightweightRecentTipSerializer


class RecentTipViewSet(ListAPIView):
    permission_classes = [IsAuthenticated]

    filterset_class = RecentTipFilter

    serializer_class = LightweightRecentTipSerializer

    pagination_class = StandardResultsSetPagination

    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        tips = Tip.objects.by_user_id(user_id=user.id)

        return tips
