from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from notifications.models import Notification
from rest_framework.generics import ListAPIView

from main.models import (
    Example,
    Student,
    Tip,
    User,
    UserStudentMapping,
)
from libs.cache import ActivityCache

from ...filters import UserGridFilter
from ...pagination import SmallResultsSetPagination
from ...permissions import IsManagerUser
from ...serializers import UserGridSerializer


class ManagerUserGridView(ListAPIView):
    permission_classes = [IsManagerUser]

    serializer_class = UserGridSerializer

    pagination_class = SmallResultsSetPagination

    filterset_class = UserGridFilter

    ordering = ["id"]

    def get_queryset(self):
        queryset = User.objects.annotate_full_name()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()

        user_ids = self.filter_queryset(self.get_queryset()).values_list(
            "id", flat=True
        )

        last_activities = ActivityCache.get_user_activities(
            user_ids, **self.request.query_params.dict()
        )
        content_types = ContentType.objects.get_for_models(
            Tip, Example
        )

        context["user_last_activity"] = self.get_user_last_activity(user_ids)
        context["user_students"] = self.get_user_students(user_ids)
        context["last_activities"] = last_activities
        context["all_action_objects"] = self.get_all_action_objects(
            last_activities, content_types
        )
        context["content_types"] = content_types

        return context

    def get_all_action_objects(self, last_activities, content_types):
        actions = {}
        for _, activity in last_activities.items():
            for action_type_id, action_objects in activity.items():
                if action_type_id not in actions:
                    actions[action_type_id] = set()

                actions[action_type_id] |= set().union(
                    *(action_object.keys() for action_object in action_objects)
                )

        tips = Tip.objects.to_dict(actions.get(content_types[Tip].id))
        examples = Example.objects.to_dict(
            actions.get(content_types[Example].id),
            select_related=["added_by", "updated_by"],
        )

        return {
            Tip: tips,
            Example: examples,
        }

    def get_user_students(self, user_ids):
        students_by_users = (
            UserStudentMapping.objects.get_users_students_dictionary(
                user_ids=user_ids
            )
        )
        student_ids = set().union(
            *(student_ids for _, student_ids in students_by_users.items())
        )
        students = Student.objects.to_dict(student_ids=student_ids)

        user_students = {}
        for user_id, student_ids in students_by_users.items():
            if user_id not in user_students:
                user_students[user_id] = []

            for student_id in student_ids:
                if student_id not in students:
                    continue

                user_students[user_id].append(students[student_id])

        return user_students

    def get_user_last_activity(self, user_ids):
        notifications = (
            Notification.objects.filter(
                recipient_id__in=user_ids, level="success"
            )
            .values("recipient_id")
            .annotate(
                last_activity=Max("timestamp"),
            )
            .order_by("recipient_id")
        )

        result = {}
        for notification in notifications:
            user_id = notification["recipient_id"]
            result[user_id] = notification["last_activity"]

        return result
