from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from reversion.views import RevisionMixin

from main.models import Student, Tip, TipRating
from tasks import notification

from ..filters import TipFilter
from ..permissions import IsAuthenticated
from ..serializers import (
    DLPTipSerializer,
    LightweightDLPTipSerializer,
    StatsTipSerializer,
    SuggestTipSerializer,
    TipSerializer,
)
from .base import BaseStandardPaginationViewSet
from .version_minxin import VersionViewMixin


class TipViewSet(
    RevisionMixin, VersionViewMixin, BaseStandardPaginationViewSet
):
    permission_classes = [IsAuthenticated]

    serializer_class = TipSerializer

    filterset_class = TipFilter

    ordering_fields = ["created_at", "id"]
    ordering = ["id"]

    def get_queryset(self):
        user = self.request.user
        queryset = Tip.objects.annotate_count_value(user.id)

        if user.is_dlp:
            queryset = Tip.objects.by_dlp(user)

        queryset = queryset.select_related(
            "updated_by", "added_by"
        ).prefetch_related("tags", "linked_tips")

        return queryset

    def get_serializer_class(self):
        user = self.request.user

        if self.action == "list" and not self.kwargs:
            if user.is_dlp:
                return LightweightDLPTipSerializer
            return StatsTipSerializer
        elif self.action == "retrieve" and user.is_dlp:
            return DLPTipSerializer
        return TipSerializer

    @action(detail=True, methods=["post"])
    def suggest(self, request, pk=None):
        data = request.data
        data["tip"] = pk
        serializer = SuggestTipSerializer(
            data=data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "created"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="try")
    def try_tip(self, request, pk=None):
        tip = get_object_or_404(Tip, pk=pk)
        user = self.request.user

        data = request.data
        helpful = data.get("helpful")
        retry_later = data.get("retry_later")

        student = Student.objects.filter(pk=data.get("student")).first()
        tip_rating = TipRating.objects.get_or_update_try_count(
            user=user, tip=tip, student=student
        )

        notification.create_notifications.delay(
            tip_rating.generate_try_tip_rating_notification()
        )

        if helpful:
            tip.helpful_count += 1
            tip.save()
        if retry_later is not None:
            TipRating.objects.get_or_update_retry_later(
                user=user, tip=tip, retry_later=retry_later
            )

        serializer = TipSerializer(instance=tip)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        tip = self.get_object()
        user = self.request.user

        tip_rating = TipRating.objects.get_or_update_read_count(
            user=user, tip=tip
        )

        notification.create_notifications.delay(
            tip_rating.generate_read_tip_rating_notification()
        )

        return super().retrieve(request, *args, **kwargs)
