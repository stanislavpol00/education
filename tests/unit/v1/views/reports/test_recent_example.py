from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory


class TestRecentExampleAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url_for_normal_user = reverse("v1:reports-recent-examples")

        cls.example1 = ExampleFactory.create(
            description="example 1", updated_by=cls.normal_user
        )
        cls.example2 = ExampleFactory.create(
            description="example 2", added_by=cls.normal_user
        )
        cls.not_in_example = ExampleFactory.create(
            description="example 3",
            added_by=cls.normal_user,
        )
        cls.not_in_example.created_at = (
            timezone.localtime() - timezone.timedelta(days=10)
        )
        cls.not_in_example.save()

        cls.other_user_example = ExampleFactory.create(description="other")

        cls.expected_keys = [
            "id",
            "tip",
            "description",
            "example_type",
            "context_notes",
            "sounds_like",
            "looks_like",
            "episode",
            "is_active",
            "goal",
            "is_workflow_completed",
            "is_bookmarked",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
            "updated_by",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
            "episode_student_id",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(
            self.url_for_normal_user, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)
        self.assertNotIn(self.not_in_example.id, ids)
        self.assertNotIn(self.other_user_example.id, ids)

    def test_get_list_success_with_filter_page_not_found(self):
        response = self.forced_authenticated_client.get(
            self.url_for_normal_user, {"page": 99999999}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected = [
            ("count", None),
            ("next", None),
            ("previous", None),
            ("results", []),
        ]
        for item in expected:
            self.assertEqual(response.data[item[0]], item[1])

    def test_get_list_success_with_user_filter(self):
        response = self.forced_authenticated_client.get(
            self.url_for_normal_user,
            {"user": self.normal_user.id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)
        self.assertNotIn(self.not_in_example.id, ids)
        self.assertNotIn(self.other_user_example.id, ids)

    def test_get_list_success_with_days_filter(self):
        response = self.forced_authenticated_client.get(
            self.url_for_normal_user, {"days": 14}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)
        self.assertIn(self.not_in_example.id, ids)
        self.assertNotIn(self.other_user_example.id, ids)

    def test_get_list_success_with_default_days_filter(self):
        response = self.forced_authenticated_client.get(
            self.url_for_normal_user, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)
        self.assertNotIn(self.not_in_example.id, ids)
        self.assertNotIn(self.other_user_example.id, ids)
