from django.urls import reverse
from django.utils import timezone

from tests.base_api_test import BaseAPITestCase
from tests.factories import TipRatingFactory


class TestTipRating(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.now = timezone.now()
        cls.tip_rating1 = TipRatingFactory.create(
            commented_at=cls.now - timezone.timedelta(days=3)
        )
        cls.tip_rating2 = TipRatingFactory.create(
            commented_at=cls.now - timezone.timedelta(days=2)
        )
        cls.tip_rating3 = TipRatingFactory.create(
            commented_at=cls.now - timezone.timedelta(days=1)
        )

        cls.all_tip_ratings = [
            cls.tip_rating1,
            cls.tip_rating2,
            cls.tip_rating3,
        ]

        cls.detail_url = reverse(
            "v1:tip-ratings-detail",
            args=[
                cls.tip_rating1.tip.id,
                cls.tip_rating1.id,
            ],
        )
        cls.update_url = reverse(
            "admin:main_tiprating_change", args=[cls.tip_rating1.id]
        )
        cls.history_url = reverse(
            "admin:main_tiprating_history", args=[cls.tip_rating1.id]
        )

        cls.list_url = reverse("admin:main_tiprating_changelist")
        cls.export_url = reverse("admin:main_tiprating_export")

    def test_get_list_view_success(self):
        response = self.super_user_client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.export_url)

        for tip_rating in self.all_tip_ratings:
            self.assertContains(response, tip_rating.comment)

    def test_get_change_view_success(self):
        response = self.super_user_client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.history_url)

    def test_post_export_data(self):
        data = {
            "file_format": "0",  # CSV
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_records = [
            self.tip_rating1.comment,
            self.tip_rating2.comment,
            self.tip_rating3.comment,
        ]
        exclude_records = []
        self._assert_export_data(
            response, "comment", include_records, exclude_records
        )

    def test_post_export_data_with_filter_by_new_comment_first(self):
        data = {
            "file_format": "0",  # CSV
            "new_comment_first": "true",
            "created_0": (self.now - timezone.timedelta(days=1)).isoformat(),
            "created_1": (self.now + timezone.timedelta(days=1)).isoformat(),
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_records = [
            self.tip_rating3.comment,
            self.tip_rating2.comment,
            self.tip_rating1.comment,
        ]
        exclude_records = []
        self._assert_export_data(
            response, "comment", include_records, exclude_records
        )

    def test_post_export_data_with_filter_by_commented(self):
        data = {
            "file_format": "0",  # CSV
            "commented_0": (self.now - timezone.timedelta(days=1)).isoformat(),
            "commented_1": (self.now + timezone.timedelta(days=1)).isoformat(),
        }

        response = self.super_user_client.post(self.export_url, data=data)

        include_records = [self.tip_rating3.comment]
        exclude_records = [self.tip_rating1.comment, self.tip_rating2.comment]
        self._assert_export_data(
            response, "comment", include_records, exclude_records
        )
