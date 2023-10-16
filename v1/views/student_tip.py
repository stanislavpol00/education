from rest_framework import mixins, viewsets

from main.models import StudentTip, TipRating
from tasks import notification

from ..filters import StudentTipFilter
from ..pagination import StandardResultsSetPagination
from ..permissions import IsAuthenticated
from ..serializers import StudentTipSerializer


class StudentTipViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = StandardResultsSetPagination

    permission_classes = [IsAuthenticated]

    serializer_class = StudentTipSerializer

    filterset_class = StudentTipFilter

    ordering_fields = ["updated_at", "id"]

    def get_queryset(self):
        student_pk = self.kwargs["student_pk"]
        user = self.request.user

        queryset = StudentTip.objects.annotate_browse_tips(
            user=user, student_id=student_pk
        )

        if user.is_dlp:
            queryset = queryset.filter(is_queued=False, student_id=student_pk)

        queryset = (
            queryset.distinct()
            .select_related("added_by", "tip", "tip__updated_by")
            .order_by("id")
        )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        student_tip = self.get_object()
        user = self.request.user

        tip_rating = TipRating.objects.get_or_update_read_count(
            user=user, tip=student_tip.tip, student=student_tip.student
        )

        notification.create_notifications.delay(
            tip_rating.generate_read_tip_rating_notification()
        )

        return super().retrieve(request, *args, **kwargs)
