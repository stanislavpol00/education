from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from main.models import Tip
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    TagFactory,
    TaggedExampleFactory,
    TaggedTipFactory,
    TipFactory,
)


class TestTaggedItemAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:tagged_items-list")

        cls.tag1 = TagFactory.create(
            name="tag 1",
            slug="slug 1",
        )

        cls.tag2 = TagFactory.create(
            name="tag 2",
            slug="slug 2",
        )

        cls.tagged_tip_item1 = TaggedTipFactory.create(tag=cls.tag1)
        cls.tagged_tip_item2 = TaggedExampleFactory.create(tag=cls.tag2)

        cls.detail_url = reverse(
            "v1:tagged_items-detail", args=[cls.tagged_tip_item1.id]
        )

        cls.expected_detail_keys = [
            "id",
            "object_id",
            "content_type",
            "tag",
        ]

    def test_get_list_success(self):
        response = self.authenticated_manager_client.get(
            self.list_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tagged_tip_item1.id, ids)
        self.assertIn(self.tagged_tip_item2.id, ids)

    def test_get_list_with_filter_tag_name(self):
        # name = tagged_tip_item1.tag.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"name": self.tag1.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tagged_tip_item1.id, ids)
        self.assertNotIn(self.tagged_tip_item2.id, ids)

        # name = tagged_tip_item2.tag.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"name": self.tag2.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tagged_tip_item1.id, ids)
        self.assertIn(self.tagged_tip_item2.id, ids)

    def test_get_list_with_filter_tag_slug(self):
        # slug = tagged_tip_item1.tag.slug
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"slug": self.tagged_tip_item1.tag.slug},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tagged_tip_item1.id, ids)
        self.assertNotIn(self.tagged_tip_item2.id, ids)

        # slug = tagged_tip_item2.tag.slug
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"slug": self.tagged_tip_item2.tag.slug},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tagged_tip_item1.id, ids)
        self.assertIn(self.tagged_tip_item2.id, ids)

    def test_get_list_with_filter_object_id(self):
        # object_id = tagged_tip_item1.object_id
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"object_id": self.tagged_tip_item1.object_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tagged_tip_item1.id, ids)
        self.assertNotIn(self.tagged_tip_item2.id, ids)

        # object_id = tagged_tip_item2.object_id
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"object_id": self.tagged_tip_item2.object_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tagged_tip_item1.id, ids)
        self.assertIn(self.tagged_tip_item2.id, ids)

    def test_get_list_with_filter_content_type(self):
        # content_type = tagged_tip_item1.content_type
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"content_type": self.tagged_tip_item1.content_type_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tagged_tip_item1.id, ids)
        self.assertNotIn(self.tagged_tip_item2.id, ids)

        # content_type = tagged_tip_item2.content_type
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"content_type": self.tagged_tip_item2.content_type_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tagged_tip_item1.id, ids)
        self.assertIn(self.tagged_tip_item2.id, ids)

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

        self.assertEqual(self.tagged_tip_item1.id, response.data["id"])
        self.assertNotEqual(self.tagged_tip_item2.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:tagged_items-detail", args=[-1])
        response = self.authenticated_manager_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_full_detail_success(self):
        tip = TipFactory.create()
        tip_content_type = ContentType.objects.get_for_model(Tip)

        data = {
            "object_id": tip.id,
            "content_type": tip_content_type.id,
            "tag": self.tag1.id,
        }

        response = self.authenticated_manager_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tagged_tip_item1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_partial_detail_success(self):
        data = {"tag": self.tag2.id}

        response = self.authenticated_manager_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tagged_tip_item1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_create_success(self):
        tip = TipFactory.create()
        tip_content_type = ContentType.objects.get_for_model(Tip)

        data = {
            "object_id": tip.id,
            "content_type": tip_content_type.id,
            "tag": self.tag1.id,
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
