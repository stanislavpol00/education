from rest_framework.generics import ListAPIView

from main.models import Example

from ...filters import RecentExampleFilter
from ...pagination import StandardResultsSetPagination
from ...permissions import IsManagerUser
from ...serializers import LightweightExampleSerializer


class ManagerRecentExampleViewSet(ListAPIView):
    permission_classes = [IsManagerUser]

    filterset_class = RecentExampleFilter

    serializer_class = LightweightExampleSerializer

    pagination_class = StandardResultsSetPagination

    ordering = ["-created_at"]

    def get_queryset(self):
        examples = Example.objects.all()
        return examples
