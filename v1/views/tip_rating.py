from rest_framework import mixins, viewsets

from main.models import TipRating

from ..filters import TipRatingFilter
from ..pagination import StandardResultsSetPagination
from ..permissions import IsAuthenticated
from ..serializers import TipRatingSerializer


class TipRatingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    pagination_class = StandardResultsSetPagination

    serializer_class = TipRatingSerializer

    filterset_class = TipRatingFilter

    search_fields = ["comment"]

    ordering_fields = ["id", "added_by", "tip"]

    def get_queryset(self):
        tip_id = self.kwargs["tip_pk"]

        queryset = (
            TipRating.objects.filter(tip_id=tip_id)
            .select_related("added_by")
            .order_by("id")
        )

        # TODO: Open this later on.
        # user = self.request.user
        # if user.is_role_admin or user.is_role_manager:
        #     return queryset

        # queryset = queryset.filter(added_by=user)

        return queryset
