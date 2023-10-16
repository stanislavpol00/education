from django.urls import reverse
from django.utils import timezone
from notifications.models import Notification
from rest_framework import status

import constants
from main.models import TipRating
from tests.base_api_test import BaseAPITestCase
from tests.factories import StudentFactory, TipRatingFactory


class TestTipRatingAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.now = timezone.now()

        cls.student1 = StudentFactory.create()

        cls.tip_rating1 = TipRatingFactory.create(
            created_at=cls.now,
            added_by=cls.normal_user,
            student=cls.student1,
        )
        cls.tip = cls.tip_rating1.tip

        cls.student2 = StudentFactory.create()
        cls.tip_rating2 = TipRatingFactory.create(
            created_at=cls.now - timezone.timedelta(days=2),
            tip=cls.tip,
            added_by=cls.manager_user,
            student=cls.student2,
        )

        cls.cannot_see_tip_rating = TipRatingFactory.create(tip=cls.tip)

        cls.start_date = cls.now - timezone.timedelta(days=1)
        cls.end_date = cls.now + timezone.timedelta(days=1)

        cls.list_url = reverse("v1:tip-ratings-list", args=[cls.tip.id])
        cls.detail_url = reverse(
            "v1:tip-ratings-detail", args=[cls.tip.id, cls.tip_rating1.id]
        )

        cls.expected_detail_keys = [
            "id",
            "tip",
            "added_by",
            "student",
            "clarity",
            "relevance",
            "uniqueness",
            "comment",
            "commented_at",
            "read_count",
            "try_count",
            "try_comment",
            "tried_at",
            "created_at",
            "updated_at",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)
        # self.assertNotIn(self.cannot_see_tip_rating.id, ids)

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
        self.assertIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)

        # start_date
        response = self.forced_authenticated_client.get(
            self.list_url, {"start_date": self.end_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip_rating1.id, ids)
        self.assertNotIn(self.tip_rating2.id, ids)

    def test_get_list_with_filter_end_date(self):
        # end_date
        response = self.forced_authenticated_client.get(
            self.list_url, {"end_date": self.end_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)

        # end_date
        response = self.forced_authenticated_client.get(
            self.list_url, {"end_date": self.start_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip_rating1.id, ids)
        self.assertNotIn(self.tip_rating2.id, ids)

    def test_get_list_with_filter_added_by(self):
        # added_by_id is from tip_rating 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"added_by": self.tip_rating1.added_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertNotIn(self.tip_rating2.id, ids)

        # added_by_id is from tip_rating 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"added_by": self.manager_user.id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)

    def test_get_list_with_filter_student(self):
        # student is from tip_rating 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"student": self.tip_rating1.student_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertNotIn(self.tip_rating2.id, ids)

        # student is from tip_rating 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"student": self.tip_rating2.student_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tip_rating1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse(
            "v1:tip-ratings-detail", args=[self.tip.id, -1]
        )
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_fail(self):
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
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
            "relevance": 2,
            "uniqueness": 4.5,
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
            reverse("v1:tip-ratings-detail", args=[self.tip.id, -1])
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_create_success(self):
        count1 = TipRating.objects.count()

        student = StudentFactory.create()
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "comment": "this is bad",
            "student": student.id,
        }

        response = self.authenticated_admin_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        count2 = TipRating.objects.count()
        self.assertEqual(count1 + 1, count2)

    def test_create_success_with_student_is_none(self):
        old_count = TipRating.objects.count()

        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "comment": "this is bad",
            "student": None,
        }

        response = self.authenticated_admin_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        new_count = TipRating.objects.count()
        self.assertEqual(old_count + 1, new_count)

    def test_create_success_with_check_comment_tip_notification(self):
        # not pass comment field
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
        }

        response = self.authenticated_admin_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        tip_rating = TipRating.objects.get(pk=response.data["id"])

        # check create notification
        is_existed = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient_id=self.admin_user.id,
            verb=constants.Activity.COMMENT_TIP,
            description="{} commented the tip {}".format(
                tip_rating.added_by.full_name,
                tip_rating.tip.title,
            ),
        ).exists()
        self.assertFalse(is_existed)

        # pass comment field
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "comment": "this is bad",
        }

        response = self.authenticated_admin_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        tip_rating.refresh_from_db()

        # check create notification
        is_existed = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient_id=self.admin_user.id,
            verb=constants.Activity.COMMENT_TIP,
            description="{} commented the tip {}".format(
                tip_rating.added_by.full_name,
                tip_rating.tip.title,
            ),
        ).exists()
        self.assertTrue(is_existed)

    def test_create_success_with_already_existing_rating_for_admin(self):
        student = StudentFactory.create()
        tip_rating = TipRatingFactory.create(
            added_by=self.admin_user,
            tip=self.tip,
            student=student,
            clarity=0,
            relevance=0,
            uniqueness=0,
        )

        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "student": student.id,
        }

        old_count = TipRating.objects.count()

        response = self.authenticated_admin_client.post(
            self.list_url, data=data, format="json"
        )

        new_count = TipRating.objects.count()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertEqual(0, new_count - old_count)

        tip_rating.refresh_from_db()
        self.assertEqual(data["clarity"], tip_rating.clarity)
        self.assertEqual(data["relevance"], tip_rating.relevance)
        self.assertEqual(data["uniqueness"], tip_rating.uniqueness)

    def test_create_success_with_already_existing_rating_for_dlp(self):
        student = StudentFactory.create()
        tip_rating = TipRatingFactory.create(
            added_by=self.experimental_user,
            tip=self.tip,
            student=student,
            clarity=0,
            relevance=0,
            uniqueness=0,
        )

        # rate second time
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "student": student.id,
        }

        old_count = TipRating.objects.count()

        response = self.authenticated_dlp_client.post(
            self.list_url, data=data, format="json"
        )

        new_count = TipRating.objects.count()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertEqual(0, new_count - old_count)

        tip_rating.refresh_from_db()
        self.assertEqual(data["clarity"], tip_rating.clarity)
        self.assertEqual(data["relevance"], tip_rating.relevance)
        self.assertEqual(data["uniqueness"], tip_rating.uniqueness)

        # rate third time
        data = {
            "clarity": 5,
            "relevance": 5,
            "uniqueness": 5,
            "student": student.id,
        }

        old_count = TipRating.objects.count()

        response = self.authenticated_dlp_client.post(
            self.list_url, data=data, format="json"
        )

        new_count = TipRating.objects.count()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertEqual(0, new_count - old_count)

        tip_rating.refresh_from_db()
        self.assertEqual(data["clarity"], tip_rating.clarity)
        self.assertEqual(data["relevance"], tip_rating.relevance)
        self.assertEqual(data["uniqueness"], tip_rating.uniqueness)

    def test_create_fail_with_student_not_found(self):
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "comment": "this is bad",
            "student": -1,
        }

        response = self.authenticated_admin_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn("student", response.data)

    def test_get_list_success_admin(self):
        response = self.authenticated_admin_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)
        self.assertIn(self.cannot_see_tip_rating.id, ids)

    def test_get_list_success_with_guest(self):
        response = self.authenticated_guest_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)
        # self.assertNotIn(self.cannot_see_tip_rating.id, ids)

    def test_get_list_with_guest_and_filter_page_not_found(self):
        response = self.authenticated_guest_client.get(
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

    def test_get_list_with_guest_and_filter_start_date(self):
        # start_date
        response = self.authenticated_guest_client.get(
            self.list_url, {"start_date": self.start_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)

        # start_date
        response = self.authenticated_guest_client.get(
            self.list_url, {"start_date": self.end_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip_rating1.id, ids)
        self.assertNotIn(self.tip_rating2.id, ids)

    def test_get_list_with_guest_filter_end_date(self):
        # end_date
        response = self.authenticated_guest_client.get(
            self.list_url, {"end_date": self.end_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)

        # end_date
        response = self.authenticated_guest_client.get(
            self.list_url, {"end_date": self.start_date.isoformat()}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip_rating1.id, ids)
        self.assertNotIn(self.tip_rating2.id, ids)

    def test_get_list_with_guest_and_filter_added_by(self):
        # added_by_id is from tip_rating 1
        response = self.authenticated_guest_client.get(
            self.list_url, {"added_by": self.tip_rating1.added_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip_rating1.id, ids)
        self.assertNotIn(self.tip_rating2.id, ids)

        # added_by_id is from tip_rating 2
        response = self.authenticated_guest_client.get(
            self.list_url, {"added_by": self.manager_user.id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip_rating1.id, ids)
        self.assertIn(self.tip_rating2.id, ids)

    def test_get_detail_success_with_guest_user(self):
        response = self.authenticated_guest_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tip_rating1.id, response.data["id"])

    def test_get_detail_not_found_with_guest_user(self):
        not_found_url = reverse(
            "v1:tip-ratings-detail", args=[self.tip.id, -1]
        )
        response = self.authenticated_guest_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_guest_and_update_full_detail_fail(self):
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "comment": "this is bad",
        }

        response = self.authenticated_guest_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_update_with_guest_and_update_partial_detail_fail(self):
        data = {
            "clarity": 1.5,
            "relevance": 2,
            "uniqueness": 4.5,
            "comment": "this is bad",
        }

        response = self.authenticated_guest_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    def test_delete_fail_with_guest_user(self):
        response = self.authenticated_guest_client.delete(
            reverse("v1:tip-ratings-detail", args=[self.tip.id, -1])
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )
