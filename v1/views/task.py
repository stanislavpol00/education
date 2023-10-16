from main.models import Task

from ..filters import TaskFilter
from ..permissions import IsAuthenticated
from ..serializers import TaskSerializer
from .base import BaseStandardPaginationViewSet


class TaskViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = TaskSerializer

    filterset_class = TaskFilter

    ordering_fields = ["created_at", "added_by", "tip", "student"]

    def get_queryset(self):
        return Task.objects.select_related("added_by").order_by("id")
