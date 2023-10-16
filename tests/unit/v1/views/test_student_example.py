from django.urls import reverse
from django.utils import timezone
from rest_framework import status

import constants
from tests.base_api_test import BaseAPITestCase
from tests.factories import StudentExampleFactory


class TestStudentExampleAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:student-examples-list")

        cls.student_example1 = StudentExampleFactory.create(
            reason=constants.StudentExample.REASON_INAPPROPRIATE
        )
        cls.student_example2 = StudentExampleFactory.create()

        cls.detail_url = reverse(
            "v1:student-examples-detail", args=[cls.student_example1.id]
        )

        cls.expected_detail_keys = [
            "id",
            "reason",
            "example",
            "student",
            "episode",
            "is_active",
            "added_by",
            "created_at",
            "updated_at",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(
            self.list_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

    def test_get_list_with_filter_page_not_found(self):
        response = self.forced_authenticated_client.get(
            self.list_url, {"page": 99999999}, format="json"
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

    def test_get_list_with_filter_reason(self):
        # reason = student_example 1
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"reason": self.student_example1.reason},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)

        # reason student_example 2
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"reason": self.student_example2.reason},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

    def test_get_list_with_filter_is_active(self):
        # is_active = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": True}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

        # is_active = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": False}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)

    def test_get_list_with_filter_example(self):
        # example student example 1
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"example": self.student_example1.example_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)

        # example student example 2
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"example": self.student_example2.example_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

    def test_get_list_with_filter_episode(self):
        # episode = self.student_example1.episode_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"episode": self.student_example1.episode_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)

        # episode = self.student_example2.episode_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"episode": self.student_example2.episode_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

    def test_get_list_with_filter_added_by(self):
        # added_by = self.student_example1.added_by_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"added_by": self.student_example1.added_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)

        # added_by = self.student_example2.added_by_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"added_by": self.student_example2.added_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

    def test_get_list_with_filter_student(self):
        # student = self.student_example1.student_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"student": self.student_example1.student_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)

        # student = self.student_example2.student_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"student": self.student_example2.student_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

    def test_get_list_with_filter_start_date(self):
        # start_date is yesterday
        yesterday = timezone.localtime() - timezone.timedelta(days=1)
        response = self.forced_authenticated_client.get(
            self.list_url, {"start_date": yesterday}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)

        # start_date is tomorrow
        tomorrow = timezone.localtime() + timezone.timedelta(days=1)
        student_example3 = StudentExampleFactory.create()
        student_example3.created_at = (
            timezone.localtime() + timezone.timedelta(days=3)
        )
        student_example3.save()
        response = self.forced_authenticated_client.get(
            self.list_url, {"start_date": tomorrow}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)
        self.assertIn(student_example3.id, ids)

    def test_get_list_with_filter_end_date(self):
        # end_date is yesterday
        yesterday = timezone.localtime() - timezone.timedelta(days=1)
        student_example3 = StudentExampleFactory.create()
        student_example3.created_at = (
            timezone.localtime() - timezone.timedelta(days=2)
        )
        student_example3.save()
        response = self.forced_authenticated_client.get(
            self.list_url, {"end_date": yesterday}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_example1.id, ids)
        self.assertNotIn(self.student_example2.id, ids)
        self.assertIn(student_example3.id, ids)

        # end_date is tomorrow
        tomorrow = timezone.localtime() + timezone.timedelta(days=1)
        response = self.forced_authenticated_client.get(
            self.list_url, {"end_date": tomorrow}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_example1.id, ids)
        self.assertIn(self.student_example2.id, ids)
        self.assertIn(student_example3.id, ids)

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(
            self.detail_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.student_example1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:student-examples-detail", args=[-1])
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_success(self):
        data = {
            "episode": self.student_example1.episode_id,
            "student": self.student_example1.student_id,
            "example": self.student_example1.example_id,
            "reason": constants.StudentExample.REASON_INAPPROPRIATE,
            "is_active": True,
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )
        self.assertNotEqual(
            self.normal_user.id, response.data["added_by"]["id"]
        )

        self.assertEqual(self.student_example1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_with_partial_detail(self):
        data = {
            "episode": self.student_example1.episode_id,
            "is_active": False,
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.student_example1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertNotEqual(
            self.normal_user.id, response.data["added_by"]["id"]
        )

    def test_delete_success(self):
        student_example3 = StudentExampleFactory.create()

        response = self.forced_authenticated_client.delete(
            reverse("v1:student-examples-detail", args=[student_example3.id])
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.forced_authenticated_client.get(
            reverse("v1:student-examples-detail", args=[student_example3.id]),
            format="json",
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:student-examples-detail", args=[-1])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_success(self):
        data = {
            "episode": self.student_example2.episode_id,
            "student": self.student_example2.student_id,
            "example": self.student_example1.example_id,
            "reason": constants.StudentExample.REASON_GENERATED,
            "is_active": True,
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertEqual(self.normal_user.id, response.data["added_by"]["id"])
        self.assertEqual(
            self.normal_user.full_name, response.data["added_by"]["full_name"]
        )

    def test_create_fail(self):
        data = {
            "episode": -1,
            "student": -1,
            "example": -1,
            "reason": constants.StudentExample.REASON_GENERATED,
            "is_active": True,
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("episode", response.data)
        self.assertIn("student", response.data)
        self.assertIn("example", response.data)
