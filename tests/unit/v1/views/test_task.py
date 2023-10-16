from django.urls import reverse
from rest_framework import status

import constants
from tests.base_api_test import BaseAPITestCase
from tests.factories import TaskFactory


class TestTaskAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:tasks-list")

        cls.task1 = TaskFactory.create(
            info="task 1", task_type=constants.TaskType.EXAMPLE
        )
        cls.task2 = TaskFactory.create(
            info="task 2", task_type=constants.TaskType.MISC
        )

        cls.detail_url = reverse("v1:tasks-detail", args=[cls.task1.id])

        cls.expected_detail_keys = [
            "id",
            "user",
            "tip",
            "student",
            "added_by",
            "task_type",
            "info",
            "reporter_note",
            "assignee_note",
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
        self.assertIn(self.task1.id, ids)
        self.assertIn(self.task2.id, ids)

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

    def test_get_list_with_filter_task_type(self):
        # task_type = self.task1.task_type
        response = self.forced_authenticated_client.get(
            self.list_url, {"task_type": self.task1.task_type}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.task1.id, ids)
        self.assertNotIn(self.task2.id, ids)

        # task_type = self.task2.task_type
        response = self.forced_authenticated_client.get(
            self.list_url, {"task_type": self.task2.task_type}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.task1.id, ids)
        self.assertIn(self.task2.id, ids)

    def test_get_list_with_filter_added_by(self):
        # added_by = self.task1.added_by_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"added_by": self.task1.added_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.task1.id, ids)
        self.assertNotIn(self.task2.id, ids)

        # added_by = self.task2.added_by_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"added_by": self.task2.added_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.task1.id, ids)
        self.assertIn(self.task2.id, ids)

    def test_get_list_with_filter_user(self):
        # user = self.task1.user_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"user": self.task1.user_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.task1.id, ids)
        self.assertNotIn(self.task2.id, ids)

        # user = self.task2.user_id
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"user": self.task2.user_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.task1.id, ids)
        self.assertIn(self.task2.id, ids)

    def test_get_list_with_filter_tip(self):
        # tip = self.task1.tip_id
        response = self.forced_authenticated_client.get(
            self.list_url, {"tip": self.task1.tip_id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.task1.id, ids)
        self.assertNotIn(self.task2.id, ids)

        # tip = self.task2.tip_id
        response = self.forced_authenticated_client.get(
            self.list_url, {"tip": self.task2.tip_id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.task1.id, ids)
        self.assertIn(self.task2.id, ids)

    def test_get_list_with_filter_student(self):
        # student = self.task1.student_id
        response = self.forced_authenticated_client.get(
            self.list_url, {"student": self.task1.student_id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.task1.id, ids)
        self.assertNotIn(self.task2.id, ids)

        # student = self.task2.student_id
        response = self.forced_authenticated_client.get(
            self.list_url, {"student": self.task2.student_id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.task1.id, ids)
        self.assertIn(self.task2.id, ids)

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(
            self.detail_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.task1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:tasks-detail", args=[-1])
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_success(self):
        data = {
            "user": self.task1.user_id,
            "tip": self.task1.tip_id,
            "student": self.task1.student_id,
            "info": "kkzzddeeff",
            "task_type": constants.TaskType.EXAMPLE,
            "reporter_note": "reporter_note 11",
            "assignee_note": "assignee_note  55",
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

        self.assertEqual(self.task1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_with_partial_detail(self):
        data = {
            "info": "kkzzddeeff",
            "task_type": constants.TaskType.EXAMPLE,
            "reporter_note": "reporter_note 222",
            "assignee_note": "assignee_note 333",
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.task1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertNotEqual(
            self.normal_user.id, response.data["added_by"]["id"]
        )

    def test_delete_success(self):
        task3 = TaskFactory.create(info="task 3")

        response = self.forced_authenticated_client.delete(
            reverse("v1:tasks-detail", args=[task3.id])
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.forced_authenticated_client.get(
            reverse("v1:tasks-detail", args=[task3.id]), format="json"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:tasks-detail", args=[-1])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_success(self):
        data = {
            "user": self.task1.user_id,
            "tip": self.task2.tip_id,
            "student": self.task1.student_id,
            "info": "kkzzddeeff",
            "task_type": constants.TaskType.EXAMPLE,
            "reporter_note": "reporter_note",
            "assignee_note": "assignee_note",
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
            "user": -1,
            "tip": -1,
            "student": -1,
            "info": "kkzzddeeff",
            "task_type": constants.TaskType.EXAMPLE,
            "reporter_note": "reporter_note",
            "assignee_note": "assignee_note",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("user", response.data)
        self.assertIn("tip", response.data)
        self.assertIn("student", response.data)
