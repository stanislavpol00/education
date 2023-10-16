from django.urls import reverse
from reversion.models import Version

from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory


class TestExample(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.example = ExampleFactory.create(description="description")
        cls.example1 = ExampleFactory.create(description="description1")
        cls.example2 = ExampleFactory.create(description="description2")

        cls.detail_url = reverse("v1:examples-detail", args=[cls.example.id])
        cls.update_url = reverse(
            "admin:main_example_change", args=[cls.example.id]
        )
        cls.history_url = reverse(
            "admin:main_example_history", args=[cls.example.id]
        )
        cls.list_url = reverse("admin:main_example_changelist")
        cls.export_url = reverse("admin:main_example_export")

    def test_get_list_view_success(self):
        response = self.super_user_client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.export_url)
        self.assertContains(response, "description")
        self.assertContains(response, "description1")
        self.assertContains(response, "description2")

    def test_change_view_success(self):
        response = self.super_user_client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.history_url)

    def test_history_view_has_versions_success(self):
        data = {"description": "new description"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        response = self.super_user_client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<table id="change-history">')

    def test_history_view_no_versions_success(self):
        response = self.super_user_client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<table id="change-history">')

    def test_get_compare_view_success(self):
        # create version 1
        data = {"description": "new description"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        # create version 2
        data = {"description": "new description 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        self.example.refresh_from_db()
        versions = Version.objects.get_for_object(self.example)

        data_params = {
            "version_id2": versions[0].id,
            "version_id1": versions[1].id,
        }
        compare_url = reverse(
            "admin:main_example_compare", args=[self.example.id]
        )

        response = self.super_user_client.get(compare_url, data=data_params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "new description")
        self.assertContains(response, "new description 1")

    def test_revert_version_success(self):
        # create version 1
        data = {"description": "new description"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        # create version 2
        data = {"description": "new description 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        self.example.refresh_from_db()

        version = Version.objects.get_for_object(self.example).last()
        version_url = reverse(
            "admin:main_example_revision", args=[self.example.id, version.id]
        )

        response = self.super_user_client.get(version_url)
        data = response.context["adminform"].form.initial
        data = {x: "" if y is None else y for (x, y) in data.items()}
        data["goal"] = "goal"
        data["shadows_response"] = "shadows_response"
        data["outcome"] = "outcome"
        data["tags"] = "tags"

        # recover
        self.super_user_client.post(version_url, data=data)
        self.example.refresh_from_db()
        self.assertEqual("new description", self.example.description)

    def test_post_export_data(self):
        data = {
            "file_format": "0",
        }
        response = self.super_user_client.post(self.export_url, data=data)

        self.assertContains(response, self.example1.headline, status_code=200)
        self.assertTrue(response.has_header("Content-Disposition"))
        self.assertEqual(response["Content-Type"], "text/csv")
