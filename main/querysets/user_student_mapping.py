from django.db import models


class UserStudentMappingQuerySet(models.QuerySet):
    def get_users_students_dictionary(self, user_ids=None):
        queryset = self

        if user_ids:
            queryset = queryset.filter(user_id__in=user_ids)

        queryset = queryset.values("user_id", "student_id")

        result = {}
        for item in queryset:
            user_id = item["user_id"]
            if user_id not in result:
                result[user_id] = []

            result[user_id].append(item["student_id"])

        return result

    def get_students(self, user_id):
        queryset = self.filter(user_id=user_id).values_list(
            "student_id", flat=True
        )

        return queryset
