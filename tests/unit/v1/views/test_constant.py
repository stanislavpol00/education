from django.urls import reverse
from rest_framework import status

from tests.base_api_test import BaseAPITestCase


class TestConstantAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url = reverse("v1:constants")

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(
            self.url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = [
            "SubStates",
            "States",
            "ExampleType",
            "Levels",
            "ChildContext",
            "Environment",
            "UserType",
            "Role",
            "Clarity",
            "Relevance",
            "TaskType",
            "HeadsUp",
            "Activity",
            "Group",
        ]
        self.assertEqual(
            sorted(expected_keys), sorted(list(response.data.keys()))
        )

        expected_inner_keys = ["name", "description"]
        for _, value in response.data.items():
            self.assertEqual(
                sorted(expected_inner_keys), sorted(list(value[0].keys()))
            )
