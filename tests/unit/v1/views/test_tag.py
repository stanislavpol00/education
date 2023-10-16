from django.urls import reverse
from rest_framework import status

from tests.base_api_test import BaseAPITestCase
from tests.factories import TagFactory


class TestTagAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:tags-list")

        cls.tag1 = TagFactory.create(
            name="tag 1",
            slug="slug 1",
        )

        cls.tag2 = TagFactory.create(
            name="tag 2",
            slug="slug 2",
        )

        cls.detail_url = reverse("v1:tags-detail", args=[cls.tag1.id])

        cls.expected_detail_keys = [
            "id",
            "name",
            "slug",
        ]

    def test_get_list_success(self):
        response = self.authenticated_manager_client.get(
            self.list_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tag1.id, ids)
        self.assertIn(self.tag2.id, ids)

    def test_get_list_with_filter_name(self):
        # name = tag1.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"name": self.tag1.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tag1.id, ids)
        self.assertNotIn(self.tag2.id, ids)

        # name = tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"name": self.tag2.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tag1.id, ids)
        self.assertIn(self.tag2.id, ids)

    def test_get_list_with_filter_slug(self):
        # slug = tag1.slug
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"slug": self.tag1.slug},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tag1.id, ids)
        self.assertNotIn(self.tag2.id, ids)

        # slug = tag2.slug
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"slug": self.tag2.slug},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tag1.id, ids)
        self.assertIn(self.tag2.id, ids)

    def test_get_list_fail_with_check_permission(self):
        response = self.forced_authenticated_client.get(self.list_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_get_detail_success(self):
        response = self.authenticated_manager_client.get(
            self.detail_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tag1.id, response.data["id"])
        self.assertNotEqual(self.tag2.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:tags-detail", args=[-1])
        response = self.authenticated_manager_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_full_detail_success(self):
        data = {
            "name": "updated name",
            "slug": "updated_slug",
        }

        response = self.authenticated_manager_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tag1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_with_partial_detail(self):
        data = {
            "name": "updated name",
        }

        response = self.authenticated_manager_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tag1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_create_success(self):
        data = {
            "name": "updated name",
            "slug": "updated_slug",
        }

        response = self.authenticated_manager_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_delete_success(self):
        response = self.authenticated_manager_client.delete(
            self.detail_url, format="json"
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
