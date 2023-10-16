from main.models import Activity

from ..filters import ActivityFilter
from ..permissions import IsOwnerOrManager
from ..serializers import ActivitySerializer
from .base import BaseStandardPaginationViewSet


class ActivityViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsOwnerOrManager]

    serializer_class = ActivitySerializer

    filterset_class = ActivityFilter

    def get_queryset(self):
        user = self.request.user

        queryset = Activity.objects.select_related("user")

        if not user.is_manager:
            queryset = queryset.filter(user_id=user.id)

        return queryset
