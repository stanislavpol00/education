from reversion.views import RevisionMixin

from main.models import Example

from ..filters import ExampleFilter
from ..permissions import IsAuthenticated
from ..serializers import ExampleSerializer, LightweightExampleSerializer
from .base import BaseStandardPaginationViewSet
from .version_minxin import VersionViewMixin


class ExampleViewSet(
    RevisionMixin, VersionViewMixin, BaseStandardPaginationViewSet
):
    permission_classes = [IsAuthenticated]

    serializer_class = ExampleSerializer

    filterset_class = ExampleFilter

    search_fields = ["description"]

    ordering_fields = ["id", "updated_by", "episode", "tip"]

    def get_serializer_class(self):
        if self.action == "list":
            return LightweightExampleSerializer
        return ExampleSerializer

    def get_queryset(self):
        return (
            Example.objects.order_by("id")
            .select_related(
                "updated_by",
                "added_by",
                "tip",
                "episode",
            )
            .prefetch_related("tags")
        )
