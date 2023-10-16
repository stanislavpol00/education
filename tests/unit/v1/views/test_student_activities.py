from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from main.models import Episode, StudentExample
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    EpisodeFactory,
    ExampleFactory,
    StudentExampleFactory,
    StudentFactory,
    StudentTipFactory,
    TipFactory,
)


class TestStudentActivitiesAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student1 = StudentFactory.create(first_name="student 1")
        cls.tip = TipFactory.create()
        StudentTipFactory(
            student=cls.student1,
            tip=cls.tip,
        )

        cls.example = ExampleFactory.create()
        student1_example = StudentExampleFactory(
            student=cls.student1,
            example=cls.example,
        )
        StudentExample.objects.filter(pk=student1_example.pk).update(
            updated_at=timezone.localtime() - timezone.timedelta(days=15)
        )

        cls.episode = EpisodeFactory(student=cls.student1)
        Episode.objects.filter(pk=cls.episode.pk).update(
            updated_at=timezone.localtime() - timezone.timedelta(days=25)
        )

        cls.student_activities_url = reverse(
            "v1:student-activities-list", args=[cls.student1.id]
        )

    def test_get_student_activities_success(self):
        response = self.forced_authenticated_client.get(
            self.student_activities_url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = {
            "tips": [],
            "examples": [],
            "episodes": [],
        }
        for key, items in response.data.items():
            result[key] = [item["id"] for item in items]

        self.assertIn(self.tip.id, result["tips"])
        self.assertIn(self.example.id, result["examples"])
        self.assertIn(self.episode.id, result["episodes"])

    def test_get_student_activities_fail(self):
        student_activities_url = reverse(
            "v1:student-activities-list", args=[-1]
        )

        response = self.forced_authenticated_client.get(student_activities_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_student_activities_success_with_filter_start_date(self):
        data_params = {
            "start_date": timezone.localtime() - timezone.timedelta(days=16)
        }
        response = self.forced_authenticated_client.get(
            self.student_activities_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = {
            "tips": [],
            "examples": [],
            "episodes": [],
        }
        for key, items in response.data.items():
            result[key] = [item["id"] for item in items]

        self.assertIn(self.tip.id, result["tips"])
        self.assertIn(self.example.id, result["examples"])
        self.assertNotIn(self.episode.id, result["episodes"])

    def test_get_student_activities_success_with_filter_end_date(self):
        data_params = {
            "end_date": timezone.localtime() - timezone.timedelta(days=16)
        }
        response = self.forced_authenticated_client.get(
            self.student_activities_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = {
            "tips": [],
            "examples": [],
            "episodes": [],
        }
        for key, items in response.data.items():
            result[key] = [item["id"] for item in items]

        self.assertNotIn(self.tip.id, result["tips"])
        self.assertNotIn(self.example.id, result["examples"])
        self.assertIn(self.episode.id, result["episodes"])
