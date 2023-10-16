from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from main.models import Student, UserStudentMapping


class AssignStudentSerializer(serializers.Serializer):
    students = serializers.JSONField()

    def validate_students(self, students):
        students_count = len(students)

        existed_students_count = Student.objects.filter(
            id__in=students
        ).count()

        if existed_students_count != students_count:
            raise serializers.ValidationError(
                _("One or more students are incorrect")
            )

        return students

    @transaction.atomic
    def save(self):
        validated_data = self.validated_data
        students = validated_data["students"]
        practitioner = self.initial_data["practitioner"]

        added_by = self.context["request"].user

        for student in students:
            UserStudentMapping.objects.get_or_create(
                student_id=student,
                user_id=practitioner,
                added_by=added_by,
            )


class UnAssignStudentSerializer(AssignStudentSerializer):
    @transaction.atomic
    def save(self):
        validated_data = self.validated_data
        students = validated_data["students"]
        practitioner = self.initial_data["practitioner"]

        for student in students:
            UserStudentMapping.objects.filter(
                student_id=student, user_id=practitioner
            ).delete()
