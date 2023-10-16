from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory, TipFactory


class TestManagerContributionAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url_for_special_user = reverse("v1:managers-contributions")

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

        # of admin and manager
        cls.tip1_of_manager = TipFactory.create(
            title="tip 1 of admin and manager",
            description="description 1 of admin and manager",
            added_by=cls.manager_user,
        )
        cls.tip1_of_manager.created_at -= timezone.timedelta(hours=24)
        cls.tip1_of_manager.save()
        cls.tip2_of_manager = TipFactory.create(
            title="tip 2 of admin and manager",
            description="description 2 of admin and manager",
            added_by=cls.manager_user,
        )

        cls.example1_of_manager = ExampleFactory.create(
            description="example 1 of admin and manager",
            added_by=cls.manager_user,
            tip=None,
            episode=None,
        )
        cls.example1_of_manager.created_at -= timezone.timedelta(hours=24)
        cls.example1_of_manager.save()

        cls.example2_of_manager = ExampleFactory.create(
            description="example 2 of admin and manager",
            added_by=cls.manager_user,
            tip=None,
            episode=None,
        )

        cls.old_example_of_manager = ExampleFactory.create(
            added_by=cls.manager_user, tip=None, episode=None
        )
        cls.old_example_of_manager.created_at -= timezone.timedelta(days=365)
        cls.old_example_of_manager.save()

        cls.other_example_of_manager = ExampleFactory.create(
            tip=None, episode=None
        )

    def test_get_success_manager_user(self):
        response = self.authenticated_manager_client.get(
            self.url_for_special_user, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        normal_user_contributions = response.data[self.normal_user.id]
        self.assertEqual(2, len(normal_user_contributions))
        self.assertEqual(1, normal_user_contributions[0]["tips"])
        self.assertEqual(1, normal_user_contributions[0]["examples"])
        self.assertEqual(1, normal_user_contributions[1]["tips"])
        self.assertEqual(1, normal_user_contributions[1]["examples"])

        manager_user_contributions = response.data[self.manager_user.id]
        self.assertEqual(1, manager_user_contributions[0]["tips"])
        self.assertEqual(1, manager_user_contributions[0]["examples"])
        self.assertEqual(1, manager_user_contributions[1]["tips"])
        self.assertEqual(1, manager_user_contributions[1]["examples"])

    def test_get_success_manager_user_with_days(self):
        params = {"days": 500}

        response = self.authenticated_manager_client.get(
            self.url_for_special_user, params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        normal_user_contributions = response.data[self.normal_user.id]
        self.assertEqual(3, len(normal_user_contributions))
        self.assertEqual(1, normal_user_contributions[0]["tips"])
        self.assertEqual(1, normal_user_contributions[0]["examples"])
        self.assertEqual(1, normal_user_contributions[1]["tips"])
        self.assertEqual(1, normal_user_contributions[1]["examples"])
        self.assertEqual(0, normal_user_contributions[2]["tips"])
        self.assertEqual(1, normal_user_contributions[2]["examples"])

        manager_user_contributions = response.data[self.normal_user.id]
        self.assertEqual(3, len(manager_user_contributions))
        self.assertEqual(1, manager_user_contributions[0]["tips"])
        self.assertEqual(1, manager_user_contributions[0]["examples"])
        self.assertEqual(1, manager_user_contributions[1]["tips"])
        self.assertEqual(1, manager_user_contributions[1]["examples"])
        self.assertEqual(0, manager_user_contributions[2]["tips"])
        self.assertEqual(1, manager_user_contributions[2]["examples"])

    def test_get_success_manager_user_with_days_and_user(self):
        params = {"days": 500, "user": self.normal_user.id}

        response = self.authenticated_manager_client.get(
            self.url_for_special_user, params, format="json"
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

    def test_get_success_manager_user_with_days_and_non_existed_user(self):
        params = {"days": 500, "user": -1}

        response = self.authenticated_manager_client.get(
            self.url_for_special_user, params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual([], response.data)

    def test_get_success_admin_user(self):
        response = self.authenticated_admin_client.get(
            self.url_for_special_user, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        normal_user_contributions = response.data[self.normal_user.id]
        self.assertEqual(2, len(normal_user_contributions))
        self.assertEqual(1, normal_user_contributions[0]["tips"])
        self.assertEqual(1, normal_user_contributions[0]["examples"])
        self.assertEqual(1, normal_user_contributions[1]["tips"])
        self.assertEqual(1, normal_user_contributions[1]["examples"])

        manager_user_contributions = response.data[self.manager_user.id]
        self.assertEqual(1, manager_user_contributions[0]["tips"])
        self.assertEqual(1, manager_user_contributions[0]["examples"])
        self.assertEqual(1, manager_user_contributions[1]["tips"])
        self.assertEqual(1, manager_user_contributions[1]["examples"])

    def test_get_success_admin_user_with_days(self):
        params = {"days": 500}

        response = self.authenticated_admin_client.get(
            self.url_for_special_user, params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        normal_user_contributions = response.data[self.normal_user.id]
        self.assertEqual(3, len(normal_user_contributions))
        self.assertEqual(1, normal_user_contributions[0]["tips"])
        self.assertEqual(1, normal_user_contributions[0]["examples"])
        self.assertEqual(1, normal_user_contributions[1]["tips"])
        self.assertEqual(1, normal_user_contributions[1]["examples"])
        self.assertEqual(0, normal_user_contributions[2]["tips"])
        self.assertEqual(1, normal_user_contributions[2]["examples"])

        manager_user_contributions = response.data[self.normal_user.id]
        self.assertEqual(3, len(manager_user_contributions))
        self.assertEqual(1, manager_user_contributions[0]["tips"])
        self.assertEqual(1, manager_user_contributions[0]["examples"])
        self.assertEqual(1, manager_user_contributions[1]["tips"])
        self.assertEqual(1, manager_user_contributions[1]["examples"])
        self.assertEqual(0, manager_user_contributions[2]["tips"])
        self.assertEqual(1, manager_user_contributions[2]["examples"])

    def test_get_success_admin_user_with_days_and_user(self):
        params = {"days": 500, "user": self.other_example.added_by.id}

        response = self.authenticated_admin_client.get(
            self.url_for_special_user, params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(1, len(response.data))
