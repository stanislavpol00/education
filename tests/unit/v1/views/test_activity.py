from django.urls import reverse
from django.utils import timezone
from rest_framework import status

import constants
from tests.base_api_test import BaseAPITestCase
from tests.factories import ActivityFactory


class TestActivityAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:activities-list")

        cls.activity1 = ActivityFactory.create(
            user=cls.normal_user,
            type=constants.Activity.TRY_TIP,
        )

        cls.activity2 = ActivityFactory.create(
            user=cls.manager_user,
            type=constants.Activity.READ_TIP,
        )
        cls.activity2.created_at -= timezone.timedelta(days=10)
        cls.activity2.save()

        cls.detail_url = reverse(
            "v1:activities-detail", args=[cls.activity1.id]
        )

        cls.expected_detail_keys = [
            "id",
            "type",
            "user",
            "meta",
            "created_at",
        ]

    def test_get_list_success_with_normal_user(self):
        response = self.forced_authenticated_client.get(
            self.list_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertNotIn(self.activity2.id, ids)

    def test_get_list_success_with_manager_user(self):
        response = self.authenticated_manager_client.get(
            self.list_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertIn(self.activity2.id, ids)

    def test_get_list_with_normal_user_filter_user(self):
        # user = normal_user
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"user": self.normal_user.id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertNotIn(self.activity2.id, ids)

        # user = manager_user
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"user": self.manager_user.id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.activity1.id, ids)
        self.assertNotIn(self.activity2.id, ids)

    def test_get_list_with_filter_start_date(self):
        # start_date = activity1.created_at
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"start_date": self.activity1.created_at},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertNotIn(self.activity2.id, ids)

        # start_date = activity2.created_at
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"start_date": self.activity2.created_at},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertIn(self.activity2.id, ids)

    def test_get_list_with_filter_end_date(self):
        # end_date = activity1.created_at
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"end_date": self.activity1.created_at},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertIn(self.activity2.id, ids)

        # end_date = activity2.created_at
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"end_date": self.activity2.created_at},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.activity1.id, ids)
        self.assertIn(self.activity2.id, ids)

    def test_get_list_with_filter_types(self):
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"types": ",".join([self.activity1.type, self.activity2.type])},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertIn(self.activity2.id, ids)

        response = self.authenticated_manager_client.get(
            self.list_url,
            {"types": ",".join([self.activity1.type])},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertNotIn(self.activity2.id, ids)

    def test_get_list_with_manager_user_filter_query(self):
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"query": ""},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.activity1.id, ids)
        self.assertIn(self.activity2.id, ids)

    def test_get_detail_success(self):
        # normal user
        response = self.forced_authenticated_client.get(
            self.detail_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.activity1.id, response.data["id"])

        # manager user
        response = self.authenticated_manager_client.get(
            self.detail_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.activity1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:activities-detail", args=[-1])
        response = self.authenticated_manager_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_success(self):
        data = {
            "type": constants.Activity.COMMENT_TIP,
            "meta": {"duration": 15},
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )
        self.assertEqual(self.normal_user.id, response.data["user"]["id"])

        self.assertEqual(self.activity1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_with_full_detail_fail(self):
        data = {
            "type": constants.Activity.COMMENT_TIP,
            "meta": {"duration": 15},
        }

        detail_url = reverse("v1:activities-detail", args=[self.activity2.id])
        response = self.authenticated_dlp_client.put(
            detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_partial_detail(self):
        data = {
            "type": constants.Activity.COMMENT_TIP,
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.activity1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_create_success(self):
        data = {
            "type": constants.Activity.COMMENT_TIP,
            "meta": {"duration": 15},
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

        self.assertEqual(self.normal_user.id, response.data["user"]["id"])
