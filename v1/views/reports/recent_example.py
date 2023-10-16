from rest_framework.generics import ListAPIView

from main.models import Example

from ...filters import RecentExampleFilter
from ...pagination import StandardResultsSetPagination
from ...permissions import IsAuthenticated
from ...serializers import LightweightExampleSerializer


class RecentExampleViewSet(ListAPIView):
    permission_classes = [IsAuthenticated]

    filterset_class = RecentExampleFilter

    serializer_class = LightweightExampleSerializer

    pagination_class = StandardResultsSetPagination

    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        examples = Example.objects.by_user_id(user_id=user.id)

        return examples
