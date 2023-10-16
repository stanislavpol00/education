from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from main.models import Student, StudentTip

from .tip import LightweightTipSerializer


class StudentTipSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField()
    is_rated = serializers.BooleanField()
    has_new_info = serializers.BooleanField()
    tip = LightweightTipSerializer()

    class Meta:
        model = StudentTip
        fields = [
            "id",
            "student_id",
            "tip",
            "is_read",
            "is_rated",
            "is_graduated",
            "has_new_info",
            "last_suggested_at",
            "is_queued",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "tip",
            "is_read",
            "is_rated",
            "has_new_info",
            "last_suggested_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["tip"].update(
            {
                "read_count": instance.read_count,
                "try_count": instance.try_count,
                "helpful_count": instance.helpful_count,
                "is_read": instance.is_read,
                "is_rated": instance.is_rated,
            }
        )

        return representation


class SuggestTipSerializer(serializers.Serializer):
    students = serializers.JSONField()
    is_queued = serializers.BooleanField(default=False)

    def validate_students(self, students):
        students_count = len(students)

        existed_clients_count = Student.objects.filter(id__in=students).count()

        if existed_clients_count != students_count:
            raise serializers.ValidationError(
                _("One or more students are incorrect")
            )

        return students

    @transaction.atomic
    def save(self):
        validated_data = self.validated_data
        students = validated_data["students"]
        tip = self.initial_data["tip"]
        is_queued = validated_data["is_queued"]

        added_by = self.context["request"].user

        for student in students:
            student_tip = StudentTip.objects.filter(
                student_id=student,
                tip_id=tip,
            ).first()

            if student_tip:
                student_tip.last_suggested_at = timezone.localtime()
                student_tip.save()
            else:
                StudentTip.objects.create(
                    student_id=student,
                    tip_id=tip,
                    added_by=added_by,
                    is_queued=is_queued,
                )
