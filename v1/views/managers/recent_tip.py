from rest_framework.generics import ListAPIView

from main.models import Tip

from ...filters import RecentTipFilter
from ...pagination import StandardResultsSetPagination
from ...permissions import IsManagerUser
from ...serializers import LightweightRecentTipSerializer


class ManagerRecentTipViewSet(ListAPIView):
    permission_classes = [IsManagerUser]

    filterset_class = RecentTipFilter

    serializer_class = LightweightRecentTipSerializer

    pagination_class = StandardResultsSetPagination

    ordering = ["-created_at"]

    def get_queryset(self):
        tips = Tip.objects.all()
        return tips
