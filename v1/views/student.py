from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django.utils import timezone
from notifications.models import Notification
from rest_framework.decorators import action
from rest_framework.response import Response

from main.models import Episode, Student, StudentTip

from ..filters import StudentFilter
from ..permissions import IsAuthenticated
from ..serializers import (
    LightweightNotificationSerializer,
    LightweightStudentSerializer,
    StudentDetailSerializer,
)
from .base import BaseStandardPaginationViewSet


class StudentViewSet(BaseStandardPaginationViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = LightweightStudentSerializer

    filterset_class = StudentFilter

    search_fields = ["first_name", "last_name"]

    ordering_fields = ["id", "first_name", "last_name", "nickname"]

    def get_queryset(self):
        queryset = Student.objects.order_by("id")

        user = self.request.user
        if user.is_role_experimental_teacher:
            queryset = queryset.filter(added_by=user)

        queryset = queryset.prefetch_related("tags")

        return queryset

    def get_serializer_class(self):
        if self.action != "list":
            return StudentDetailSerializer
        return LightweightStudentSerializer

    @action(detail=True, url_path="heads-up")
    def heads_up(self, request, pk=None):
        instance = self.get_object()

        return Response(instance.heads_up)

    @action(detail=True)
    def notifications(self, request, pk=None):
        user = request.user

        start_date = request.query_params.get(
            "start_date", timezone.localtime() - timezone.timedelta(days=30)
        )
        end_date = request.query_params.get("end_date", None)
        content_type_id = request.query_params.get("content_type_id", None)
        student_content_type = ContentType.objects.get_for_model(Student)

        notifications = Notification.objects.filter(
            target_object_id=pk,
            target_content_type_id=student_content_type.id,
            timestamp__gte=start_date,
            level="info",
        )

        if end_date:
            notifications = notifications.filter(timestamp__lt=end_date)
        if content_type_id:
            notifications = notifications.filter(
                action_object_content_type_id=content_type_id
            )

        if not user.is_manager:
            notifications = notifications.filter(recipient_id=user.id)

        serializer = LightweightNotificationSerializer(
            notifications, many=True
        )

        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "list":
            context["student_tips"] = StudentTip.objects.count_by_days()
            context["student_episodes"] = Episode.objects.count_by_days()
            context[
                "last_activity_timestamps_on_students"
            ] = self.get_last_activity_timestamps_on_students()

        return context

    def get_last_activity_timestamps_on_students(self):
        student_content_type_id = ContentType.objects.get_for_model(Student).id

        notifications = (
            Notification.objects.filter(
                recipient_id=self.request.user.id,
                target_content_type_id=student_content_type_id,
            )
            .values("target_object_id")
            .annotate(last_activity_timestamp=Max("timestamp"))
            .order_by("target_object_id")
        )

        result = {}
        for notification in notifications:
            student_id = int(notification["target_object_id"])
            result[student_id] = notification["last_activity_timestamp"]

        return result
