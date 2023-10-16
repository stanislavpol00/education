from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory, TipFactory


class TestContributionAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url_for_normal_user = reverse("v1:reports-contributions")

        cls.tip1 = TipFactory.create(
            title="tip 1",
            description="description 1",
            added_by=cls.normal_user,
        )
        cls.tip1.created_at -= timezone.timedelta(hours=24)
        cls.tip1.save()
        cls.tip2 = TipFactory.create(
            title="tip 2",
            description="description 2",
            added_by=cls.normal_user,
        )

        cls.example1 = ExampleFactory.create(
            description="example 1",
            added_by=cls.normal_user,
            tip=None,
            episode=None,
        )
        cls.example1.created_at -= timezone.timedelta(hours=24)
        cls.example1.save()

        cls.example2 = ExampleFactory.create(
            description="example 2",
            added_by=cls.normal_user,
            tip=None,
            episode=None,
        )

        cls.old_example = ExampleFactory.create(
            added_by=cls.normal_user, tip=None, episode=None
        )
        cls.old_example.created_at -= timezone.timedelta(days=365)
        cls.old_example.save()

        cls.other_example = ExampleFactory.create(tip=None, episode=None)

    def test_get_success_normal_user(self):
        response = self.forced_authenticated_client.get(
            self.url_for_normal_user, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        self.assertEqual(2, len(data))
        self.assertEqual(1, data[0]["tips"])
        self.assertEqual(1, data[0]["examples"])
        self.assertEqual(1, data[1]["tips"])
        self.assertEqual(1, data[1]["examples"])

    def test_get_success_normal_user_with_days(self):
        params = {"days": 500}

        response = self.forced_authenticated_client.get(
            self.url_for_normal_user, params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        self.assertEqual(3, len(data))
        self.assertEqual(1, data[0]["tips"])
        self.assertEqual(1, data[0]["examples"])
        self.assertEqual(1, data[1]["tips"])
        self.assertEqual(1, data[1]["examples"])
        self.assertEqual(0, data[2]["tips"])
        self.assertEqual(1, data[2]["examples"])
