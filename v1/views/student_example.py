from main.models import StudentExample

from ..filters import StudentExampleFilter
from ..permissions import IsAuthenticated
from ..serializers import StudentExampleSerializer
from .base import BaseStandardPaginationViewSet


class StudentExampleViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = StudentExampleSerializer

    filterset_class = StudentExampleFilter

    ordering_fields = [
        "id",
        "example",
        "student",
        "episode",
        "added_by",
    ]

    def get_queryset(self):
        queryset = StudentExample.objects.order_by("id").select_related(
            "example", "student", "episode", "added_by"
        )

        return queryset
