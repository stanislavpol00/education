from main.models import Episode

from ..filters import StudentEpisodeFilter
from ..permissions import IsAuthenticated
from ..serializers import StudentEpisodeSerializer
from .base import BaseStandardPaginationViewSet


class StudentEpisodeViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = StudentEpisodeSerializer

    filterset_class = StudentEpisodeFilter

    search_fields = ["description"]

    ordering_fields = ["id", "student", "user", "date"]

    def get_queryset(self):
        student_id = self.kwargs["student_pk"]
        return (
            Episode.objects.filter(student_id=student_id)
            .select_related("user", "practitioner")
            .prefetch_related("example_set", "example_set__added_by")
            .order_by("id")
        )
