from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from tests.base_api_test import BaseAPITestCase
from tests.factories import TipFactory, TipRatingFactory


class TestTopRatedTipAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url = reverse("v1:reports-top-rated-tips")

        cls.tip1 = TipFactory.create(
            title="tip 1",
            description="description 1",
            updated_by=cls.normal_user,
        )
        cls.tip2 = TipFactory.create(
            title="tip 2",
            description="description 2",
            updated_by=cls.normal_user,
        )
        cls.not_rated_tip = TipFactory.create(
            title="tip -1",
            description="description -1",
            updated_by=cls.normal_user,
            created_at=timezone.localtime() - timezone.timedelta(days=10),
        )

        TipRatingFactory.create(tip=cls.tip1)
        TipRatingFactory.create(tip=cls.tip2)

        cls.expected_keys = [
            "id",
            "title",
            "state",
            "levels",
            "updated_by",
            "added_by",
            "created_at",
            "average_rating",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(
            self.url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        tip = response.data[0]
        self.assertEqual(sorted(self.expected_keys), sorted(tip.keys()))

        ids = [item["id"] for item in response.data]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertNotIn(self.not_rated_tip.id, ids)

    def test_get_list_success_with_limit(self):
        TipRatingFactory.create_batch(size=10)

        response = self.forced_authenticated_client.get(
            self.url, {"limit": 5}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, len(response.data))
