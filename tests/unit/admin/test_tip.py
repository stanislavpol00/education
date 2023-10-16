from django.urls import reverse
from django.utils import timezone
from reversion.models import Version

from tests.base_api_test import BaseAPITestCase
from tests.factories import TipFactory, TipRatingFactory


class TestTip(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Not read tip
        cls.tip = TipFactory.create(title="title")
        # Read tip, but not rating and tried
        cls.tip1 = TipFactory.create(title="title1")
        # Read, rating tip, but not tried
        cls.tip2 = TipFactory.create(title="title2")
        # Read, tried tip, but not rating
        cls.tip3 = TipFactory.create(title="title3")
        # Read, tried, rating tip
        cls.tip4 = TipFactory.create(title="title4")

        cls.all_tips = [cls.tip, cls.tip1, cls.tip2, cls.tip3, cls.tip4]

        # Tip Rating for tip 1: read but not rating and tried
        TipRatingFactory.create(
            tip=cls.tip1,
            read_count=1,
            try_count=0,
            clarity=0,
            relevance=0,
            uniqueness=0,
        )
        # Tip Rating for tip 2: read, rating but not tried
        TipRatingFactory.create(
            tip=cls.tip2,
            read_count=1,
            try_count=0,
            clarity=1,
            relevance=2,
            uniqueness=0,
        )
        # Tip Rating for tip 3: read, tried but not rating
        TipRatingFactory.create(
            tip=cls.tip3,
            read_count=1,
            try_count=1,
            clarity=0,
            relevance=0,
            uniqueness=0,
        )
        # Tip Rating for tip 4: read, tried, rating
        TipRatingFactory.create(
            tip=cls.tip4,
            read_count=1,
            try_count=1,
            clarity=0,
            relevance=1,
            uniqueness=0,
        )

        cls.detail_url = reverse("v1:tips-detail", args=[cls.tip.id])
        cls.update_url = reverse("admin:main_tip_change", args=[cls.tip.id])
        cls.history_url = reverse("admin:main_tip_history", args=[cls.tip.id])

        cls.list_url = reverse("admin:main_tip_changelist")
        cls.export_url = reverse("admin:main_tip_export")

    def test_get_list_view_success(self):
        response = self.super_user_client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.export_url)

        for tip in self.all_tips:
            self.assertContains(response, tip.title)

    def test_get_change_view_success(self):
        response = self.super_user_client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.history_url)

    def test_get_history_view_has_versions_success(self):
        data = {"title": "new title"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        response = self.super_user_client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<table id="change-history">')

    def test_get_history_view_no_versions_success(self):
        response = self.super_user_client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<table id="change-history">')

    def test_get_compare_view_success(self):
        # create version 1
        data = {"title": "new title"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        # create version 2
        data = {"title": "new title 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        self.tip.refresh_from_db()
        versions = Version.objects.get_for_object(self.tip)

        data_params = {
            "version_id2": versions[0].id,
            "version_id1": versions[1].id,
        }
        compare_url = reverse("admin:main_tip_compare", args=[self.tip.id])

        response = self.super_user_client.get(compare_url, data=data_params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "new title")
        self.assertContains(response, "new title 1")

    def test_revert_version_success(self):
        # create version 1
        data = {"title": "new title"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        # create version 2
        data = {"title": "new title 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        self.tip.refresh_from_db()

        version = Version.objects.get_for_object(self.tip).last()
        version_url = reverse(
            "admin:main_tip_revision", args=[self.tip.id, version.id]
        )

        response = self.super_user_client.get(version_url)
        data = response.context["adminform"].form.initial
        data = {x: "" if y is None else y for (x, y) in data.items()}
        data["child_context"] = '{"a": 1}'
        data["environment_context"] = '{"a": 1}'
        data["note"] = "note"
        data["tags"] = "tag"

        # recover
        self.super_user_client.post(version_url, data=data)
        self.tip.refresh_from_db()
        self.assertEqual("new title", self.tip.title)

    def test_post_export_data(self):
        data = {
            "file_format": "0",  # CSV
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_ids = [
            self.tip.id,
            self.tip1.id,
            self.tip2.id,
            self.tip3.id,
            self.tip4.id,
        ]
        exclude_ids = []
        self._assert_export_data_by_id(response, include_ids, exclude_ids)

    def test_post_export_data_with_filter_by_is_read(self):
        data = {
            "file_format": "0",  # CSV
            "is_read": "true",
            "created_0": (
                timezone.now() - timezone.timedelta(days=1)
            ).isoformat(),
            "created_1": (
                timezone.now() + timezone.timedelta(days=1)
            ).isoformat(),
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_ids = [self.tip1.id, self.tip2.id, self.tip3.id, self.tip4.id]
        exclude_ids = [self.tip.id]
        self._assert_export_data_by_id(response, include_ids, exclude_ids)

    def test_post_export_data_with_filter_by_is_rating(self):
        data = {
            "file_format": "0",  # CSV
            "is_rating": "true",
            "created_0": (
                timezone.now() - timezone.timedelta(days=1)
            ).isoformat(),
            "created_1": (
                timezone.now() + timezone.timedelta(days=1)
            ).isoformat(),
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_ids = [self.tip2.id, self.tip4.id]
        exclude_ids = [self.tip.id, self.tip1.id, self.tip3.id]
        self._assert_export_data_by_id(response, include_ids, exclude_ids)

    def test_post_export_data_with_filter_by_tried(self):
        data = {
            "file_format": "0",  # CSV
            "tried": "true",
            "created_0": (
                timezone.now() - timezone.timedelta(days=1)
            ).isoformat(),
            "created_1": (
                timezone.now() + timezone.timedelta(days=1)
            ).isoformat(),
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_ids = [self.tip3.id, self.tip4.id]
        exclude_ids = [self.tip.id, self.tip1.id, self.tip2.id]
        self._assert_export_data_by_id(response, include_ids, exclude_ids)

    def test_post_export_data_with_all_filters(self):
        data = {
            "file_format": "0",  # CSV
            "is_read": "true",
            "is_rating": "true",
            "tried": "true",
            "created_0": (
                timezone.now() - timezone.timedelta(days=1)
            ).isoformat(),
            "created_1": (
                timezone.now() + timezone.timedelta(days=1)
            ).isoformat(),
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_ids = [self.tip4.id]
        exclude_ids = [self.tip.id, self.tip1.id, self.tip2.id, self.tip3.id]
        self._assert_export_data_by_id(response, include_ids, exclude_ids)
