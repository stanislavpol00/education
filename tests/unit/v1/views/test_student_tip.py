from django.urls import reverse
from django.utils import timezone
from rest_framework import status

import constants
from main.models import TipRating
from tasks import dequeue_student_tips
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    EpisodeFactory,
    StudentTipFactory,
    UserStudentMappingFactory,
)


class TestStudentTipAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.now = timezone.now()

        cls.student_tip1 = StudentTipFactory.create(is_queued=False)
        cls.student_tip1.last_used_at = cls.now
        cls.student_tip1.save()

        cls.student_tip2 = StudentTipFactory.create(
            student=cls.student_tip1.student, is_queued=False
        )
        cls.student_tip2.created_at = cls.now - timezone.timedelta(days=2)
        cls.student_tip2.last_used_at = cls.now - timezone.timedelta(days=2)
        cls.student_tip2.save()

        cls.student_tip3 = StudentTipFactory.create(
            student=cls.student_tip1.student, is_queued=True
        )

        cls.episode = EpisodeFactory.create(student=cls.student_tip1.student)

        UserStudentMappingFactory.create(
            user=cls.experimental_user,
            student=cls.student_tip1.student,
            added_by=cls.manager_user,
        )

        cls.list_url = reverse(
            "v1:student-tips-list", args=[cls.student_tip1.student_id]
        )
        cls.detail_url = reverse(
            "v1:student-tips-detail",
            args=[cls.student_tip1.student_id, cls.student_tip1.id],
        )

        cls.start_date = cls.now - timezone.timedelta(days=1)

        cls.end_date = cls.now + timezone.timedelta(days=1)

        cls.expected_detail_keys = [
            "id",
            "student_id",
            "tip",
            "is_read",
            "is_rated",
            "is_graduated",
            "has_new_info",
            "last_suggested_at",
            "is_queued",
        ]

    def test_get_list_success(self):
        dequeue_student_tips(number_of_tips=9999)
        response = self.authenticated_dlp_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)
        self.assertIn(self.student_tip3.id, ids)

    def test_get_list_success_with_manager_role(self):
        response = self.authenticated_manager_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)
        self.assertIn(self.student_tip3.id, ids)

    def test_get_list_success_with_manager_role_filter_is_queued(self):
        # is_queued = False
        response = self.authenticated_manager_client.get(
            self.list_url, data={"is_queued": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)
        self.assertNotIn(self.student_tip3.id, ids)

        # is_queued = True
        response = self.authenticated_manager_client.get(
            self.list_url, data={"is_queued": True}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)
        self.assertIn(self.student_tip3.id, ids)

    def test_get_list_with_filter_page_not_found(self):
        response = self.authenticated_dlp_client.get(
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

    def test_get_list_with_filter_tip(self):
        dequeue_student_tips(number_of_tips=9999)
        # tip = student 1
        response = self.authenticated_dlp_client.get(
            self.list_url, {"tip": self.student_tip1.tip_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

        # tip student X
        response = self.authenticated_dlp_client.get(
            self.list_url, {"tip": self.student_tip2.tip_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)

    def test_get_list_with_filter_added_by(self):
        dequeue_student_tips(number_of_tips=9999)
        # added_by = student 1
        response = self.authenticated_dlp_client.get(
            self.list_url, {"added_by": self.student_tip1.added_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

        # added_by student X
        response = self.authenticated_dlp_client.get(
            self.list_url, {"added_by": self.student_tip2.added_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)

    def test_get_list_with_filter_title(self):
        dequeue_student_tips(number_of_tips=9999)
        # title = student 1
        response = self.authenticated_dlp_client.get(
            self.list_url, {"title": self.student_tip1.tip.title}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

        # title student X
        response = self.authenticated_dlp_client.get(
            self.list_url, {"title": self.student_tip2.tip.title}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)

    def test_get_list_with_filter_description(self):
        dequeue_student_tips(number_of_tips=9999)
        # description = student 1
        response = self.authenticated_dlp_client.get(
            self.list_url, {"description": self.student_tip1.tip.description}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

        # description student X
        response = self.authenticated_dlp_client.get(
            self.list_url, {"description": self.student_tip2.tip.description}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)

    def test_get_list_with_filter_start_date(self):
        dequeue_student_tips(number_of_tips=9999)
        # start_date
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"start_date": self.start_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)

        # start_date is end_date
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"start_date": self.end_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

    def test_get_list_with_filter_end_date(self):
        dequeue_student_tips(number_of_tips=9999)
        # end_date = True
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"end_date": self.end_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)

        # end_date = False
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"end_date": self.start_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student_tip1.id, ids)
        self.assertIn(self.student_tip2.id, ids)

    def test_search_text_and_search_fields(self):
        tip1 = self.student_tip1.tip
        tip1.sub_goal = "SUB_GOAL_TEST"
        tip1.save()

        # search_text is sub_goal of tip 1 - with search_fields as sub_goal
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"search_text": tip1.sub_goal, "search_fields": "sub_goal"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

        # search_text is sub_goal of tip 1 - with search_fields as description
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"search_text": tip1.sub_goal, "search_fields": "description"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data["results"]))

        # search_text is new environment_context
        tip1.child_context = {
            constants.ChildContext.CURRENT_MOTIVATOR: "CHILD_CONTEXT_TEST",
            constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
        }
        tip1.environment_context = {
            constants.Environment.SPACE_OPPORTUNITIES: "ENVIRONMENT_CONTEXT_TEST",
            constants.Environment.SPACE_EXPECTATIONS: "new",
        }
        tip1.save()

        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"search_text": "ENVIRONMENT_CONTEXT_TEST"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

        # search_text is new environment_context - search_fields is not environment_context
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {
                "search_text": "ENVIRONMENT_CONTEXT_TEST",
                "search_fields": "description,title",
            },
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data["results"]))

        # search_text is new child_context
        response = self.authenticated_dlp_client.get(
            self.list_url, {"search_text": "CHILD_CONTEXT_TEST"}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student_tip1.id, ids)
        self.assertNotIn(self.student_tip2.id, ids)

        # search_text is new child_context - search_fields is not child_context
        response = self.authenticated_dlp_client.get(
            self.list_url,
            {
                "search_text": "ENVIRONMENT_CONTEXT_TEST",
                "search_fields": "description,title,sub_goal",
            },
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data["results"]))

    def test_get_detail_success(self):
        dequeue_student_tips(number_of_tips=9999)
        response = self.authenticated_dlp_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.student_tip1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse(
            "v1:student-tips-detail", args=[self.student_tip1.student_id, -1]
        )
        response = self.authenticated_dlp_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_success_with_check_read_count(self):
        is_existed = TipRating.objects.filter(
            added_by=self.manager_user,
            tip=self.student_tip1.tip,
            student=self.student_tip1.student,
        ).exists()
        self.assertFalse(is_existed)

        # first call main
        response = self.authenticated_manager_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tip_rating = TipRating.objects.filter(
            added_by=self.manager_user,
            tip=self.student_tip1.tip,
            student=self.student_tip1.student,
        ).first()

        self.assertEqual(tip_rating.read_count, 1)

        # second call main
        response = self.authenticated_manager_client.get(self.detail_url)

        tip_rating.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tip_rating.read_count, 2)

    def test_update_with_partial_detail_success(self):
        dequeue_student_tips(number_of_tips=9999)
        data = {
            "is_graduated": False,
        }

        response = self.authenticated_dlp_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(False, response.data["is_graduated"])

        data = {
            "is_graduated": True,
        }

        response = self.authenticated_dlp_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(True, response.data["is_graduated"])

    def test_delete_fail(self):
        response = self.authenticated_dlp_client.delete(
            reverse(
                "v1:student-tips-detail",
                args=[self.student_tip1.student_id, self.student_tip1.id],
            )
        )

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )
