from django.urls import reverse
from rest_framework import status

from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory, ExampleRatingFactory


class TestRecentExampleAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url = reverse("v1:reports-top-rated-examples")

        cls.example1 = ExampleFactory.create(
            description="example 1", updated_by=cls.normal_user
        )
        cls.example2 = ExampleFactory.create(
            description="example 2", added_by=cls.normal_user
        )
        cls.not_rated_example = ExampleFactory.create(
            description="example 2",
            added_by=cls.normal_user,
        )

        ExampleRatingFactory.create(example=cls.example1)
        ExampleRatingFactory.create(example=cls.example2)

        cls.expected_keys = [
            "example",
            "average_rating",
            "clarity_average_rating",
            "recommended_average_rating",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(
            self.url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        example = response.data[0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["example"] for item in response.data]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)
        self.assertNotIn(self.not_rated_example.id, ids)

    def test_get_list_success_with_limit(self):
        ExampleRatingFactory.create_batch(size=12)

        response = self.forced_authenticated_client.get(
            self.url, {"limit": 5}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, len(response.data))

        response = self.forced_authenticated_client.get(
            self.url,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(10, len(response.data))
