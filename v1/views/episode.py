from main.models import Episode

from ..filters import EpisodeFilter
from ..permissions import IsAuthenticated
from ..serializers import EpisodeSerializer
from .base import BaseStandardPaginationViewSet


class EpisodeViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = EpisodeSerializer

    filterset_class = EpisodeFilter

    search_fields = ["description"]

    ordering_fields = ["id", "student", "user", "date"]

    def get_queryset(self):
        queryset = (
            Episode.objects.select_related("user", "practitioner")
            .prefetch_related(
                "example_set",
                "example_set__added_by",
                "tags",
            )
            .order_by("id")
        )

        return queryset
