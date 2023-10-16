from main.models import Timeline

from ..filters import TimelineFilter
from ..permissions import IsAuthenticated
from ..serializers import TimelineSerializer
from .base import BaseStandardPaginationViewSet


class TimelineViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = TimelineSerializer

    filterset_class = TimelineFilter

    ordering_fields = ["id", "name", "days"]

    def get_queryset(self):
        return Timeline.objects.order_by("id")
