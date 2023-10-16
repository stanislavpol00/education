from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from tests.base_api_test import BaseAPITestCase
from tests.factories import TipFactory


class TestManagerRecentTipAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url_for_special_user = reverse("v1:managers-recent-tips")

        cls.tip1 = TipFactory.create(
            title="tip 1",
            description="description 1",
            added_by=cls.normal_user,
        )
        cls.tip2 = TipFactory.create(
            title="tip 2",
            description="description 2",
            updated_by=cls.normal_user,
        )
        cls.not_in_tip = TipFactory.create(
            title="tip -1",
            description="description -1",
            added_by=cls.normal_user,
            created_at=timezone.localtime() - timezone.timedelta(days=10),
        )
        cls.not_in_tip.created_at = timezone.localtime() - timezone.timedelta(
            days=10
        )
        cls.not_in_tip.save()

        cls.other_user_tip = TipFactory.create()

        cls.expected_keys = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "added_by",
            "updated_by",
            "created_at",
            "tip_summary",
        ]

    def test_get_list_success_with_manager(self):
        response = self.authenticated_manager_client.get(
            self.url_for_special_user, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        tip = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(tip.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertNotIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_success_by_manager_with_filter_page_not_found(self):
        response = self.authenticated_manager_client.get(
            self.url_for_special_user, {"page": 99999999}, format="json"
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

    def test_get_list_success_with_manager_with_user_filter(self):
        response = self.authenticated_manager_client.get(
            self.url_for_special_user,
            {"user": self.other_user_tip.added_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        tip = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(tip.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertNotIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_success_by_manager_with_days_filter(self):
        response = self.authenticated_manager_client.get(
            self.url_for_special_user,
            {"days": 14},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_success_by_manager_with_default_days_filter(self):
        response = self.authenticated_manager_client.get(
            self.url_for_special_user,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertNotIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_success_with_admin(self):
        response = self.authenticated_manager_client.get(
            self.url_for_special_user, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        tip = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(tip.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertNotIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_success_by_admin_with_filter_page_not_found(self):
        response = self.authenticated_admin_client.get(
            self.url_for_special_user, {"page": 99999999}, format="json"
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

    def test_get_list_success_with_admin_with_user_filter(self):
        response = self.authenticated_admin_client.get(
            self.url_for_special_user,
            {"user": self.other_user_tip.added_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        tip = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(tip.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertNotIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_success_by_admin_with_days_filter(self):
        response = self.authenticated_admin_client.get(
            self.url_for_special_user,
            {"days": 14},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_success_by_admin_with_default_days_filter(self):
        response = self.authenticated_admin_client.get(
            self.url_for_special_user,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        example = response.data["results"][0]
        self.assertEqual(sorted(self.expected_keys), sorted(example.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertNotIn(self.not_in_tip.id, ids)
        self.assertIn(self.other_user_tip.id, ids)

    def test_get_list_fail_with_check_permissions(self):
        response = self.forced_authenticated_client.get(
            self.url_for_special_user, format="json"
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
