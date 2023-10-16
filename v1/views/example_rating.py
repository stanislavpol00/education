from rest_framework import mixins, viewsets

from main.models import ExampleRating

from ..filters import ExampleRatingFilter
from ..pagination import StandardResultsSetPagination
from ..permissions import IsAuthenticated
from ..serializers import ExampleRatingSerializer


class ExampleRatingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    pagination_class = StandardResultsSetPagination

    serializer_class = ExampleRatingSerializer

    filterset_class = ExampleRatingFilter

    search_fields = ["comment"]

    ordering_fields = ["id", "added_by", "example"]

    def get_queryset(self):
        example_id = self.kwargs["example_pk"]

        queryset = (
            ExampleRating.objects.filter(example_id=example_id)
            .select_related("added_by")
            .order_by("id")
        )

        # TODO: Open this later on.
        # user = self.request.user
        # if user.is_role_admin or user.is_role_manager:
        #     return queryset

        # queryset = queryset.filter(added_by=user)

        return queryset
