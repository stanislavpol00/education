from main.models import Example

from ..filters import EpisodeExampleFilter
from ..permissions import IsAuthenticated
from ..serializers import EpisodeExampleSerializer
from .base import BaseStandardPaginationViewSet


class EpisodeExampleViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = EpisodeExampleSerializer

    filterset_class = EpisodeExampleFilter

    search_fields = ["description"]

    ordering_fields = ["id", "updated_by", "episode", "tip"]

    def get_queryset(self):
        episode_id = self.kwargs["episode_pk"]
        return (
            Example.objects.filter(episode_id=episode_id)
            .order_by("id")
            .select_related(
                "updated_by",
            )
        )
