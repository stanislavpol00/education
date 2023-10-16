from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from main.models import ExampleRating
from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleRatingFactory


class TestExampleRatingAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.now = timezone.now()

        cls.example_rating1 = ExampleRatingFactory.create(
            created_at=cls.now, added_by=cls.normal_user
        )
        cls.example = cls.example_rating1.example
        cls.example_rating2 = ExampleRatingFactory.create(
            created_at=cls.now - timezone.timedelta(days=2),
            example=cls.example,
            added_by=cls.normal_user,
        )

        cls.cannot_see_example_rating = ExampleRatingFactory.create(
            example=cls.example
        )

        cls.start_date = cls.now - timezone.timedelta(days=1)
        cls.end_date = cls.now + timezone.timedelta(days=1)

        cls.list_url = reverse(
            "v1:example-ratings-list", args=[cls.example.id]
        )
        cls.detail_url = reverse(
            "v1:example-ratings-detail",
            args=[cls.example.id, cls.example_rating1.id],
        )

        cls.expected_detail_keys = [
            "id",
            "example",
            "added_by",
            "clarity",
            "recommended",
            "comment",
            "created_at",
            "updated_at",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example_rating1.id, ids)
        self.assertIn(self.example_rating2.id, ids)
        # self.assertNotIn(self.cannot_see_example_rating.id, ids)

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

    def test_get_list_with_filter_start_date(self):
        # start_date
        response = self.forced_authenticated_client.get(
            self.list_url, {"start_date": self.start_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example_rating1.id, ids)
        self.assertIn(self.example_rating2.id, ids)

        # start_date
        response = self.forced_authenticated_client.get(
            self.list_url, {"start_date": self.end_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example_rating1.id, ids)
        self.assertNotIn(self.example_rating2.id, ids)

    def test_get_list_with_filter_end_date(self):
        # end_date
        response = self.forced_authenticated_client.get(
            self.list_url, {"end_date": self.end_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example_rating1.id, ids)
        self.assertIn(self.example_rating2.id, ids)

        # end_date
        response = self.forced_authenticated_client.get(
            self.list_url, {"end_date": self.start_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example_rating1.id, ids)
        self.assertNotIn(self.example_rating2.id, ids)

    def test_get_list_with_filter_added_by(self):
        # added_by_id is from example_rating 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"added_by": self.example_rating1.added_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example_rating1.id, ids)
        self.assertIn(self.example_rating2.id, ids)

        # added_by_id is from example_rating 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"added_by": self.admin_user.id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example_rating1.id, ids)
        self.assertNotIn(self.example_rating2.id, ids)

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.example_rating1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse(
            "v1:example-ratings-detail", args=[self.example.id, -1]
        )
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_fail(self):
        data = {
            "clarity": 1.5,
            "recommended": 4.5,
            "comment": "this is bad",
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_update_with_partial_detail_fail(self):
        data = {
            "clarity": 1.5,
            "recommended": 4.5,
            "comment": "this is bad",
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:example-ratings-detail", args=[self.example.id, -1])
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_create_success(self):
        old_examples_count = ExampleRating.objects.count()

        data = {
            "clarity": 1.5,
            "recommended": 4.5,
            "comment": "this is bad",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        new_examples_count = ExampleRating.objects.count()
        self.assertEqual(old_examples_count + 1, new_examples_count)

    def test_get_list_success_admin(self):
        response = self.authenticated_admin_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example_rating1.id, ids)
        self.assertIn(self.example_rating2.id, ids)
        self.assertIn(self.cannot_see_example_rating.id, ids)
