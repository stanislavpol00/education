from django.contrib.contenttypes.models import ContentType
from django.db.models import Max, signals
from django.urls import reverse
from django.utils import timezone
from factory.django import mute_signals
from notifications.models import Notification
from rest_framework import status

import constants
from main.models import Student, Tip, User
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    EpisodeFactory,
    StudentFactory,
    StudentTipFactory,
    TagFactory,
    TaggedStudentFactory,
    UserFactory,
    UserStudentMappingFactory,
)


class TestStudentAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:students-list")

        cls.student1 = StudentFactory.create(
            first_name="student 1",
            added_by=cls.normal_user,
        )
        cls.student2 = StudentFactory.create(first_name="student 2")

        cls.detail_url = reverse("v1:students-detail", args=[cls.student1.id])
        cls.heads_up_url = reverse(
            "v1:students-heads-up", args=[cls.student1.id]
        )

        cls.create_student_notifications()
        cls.student_notifications_url = reverse(
            "v1:students-notifications", args=[cls.student1.id]
        )

        cls.expected_list_keys = [
            "id",
            "first_name",
            "last_name",
            "nickname",
            "is_active",
            "image",
            "visible_for_guest",
            "created_at",
            "updated_at",
            "number_of_tips",
            "number_of_episodes",
            "last_activity_timestamp",
        ]

        cls.expected_detail_keys = [
            "id",
            "first_name",
            "last_name",
            "nickname",
            "is_active",
            "image",
            "visible_for_guest",
            "last_month_heads_up",
            "monitoring",
            "created_at",
            "updated_at",
            "tags",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))
        self.assertEqual(
            sorted(self.expected_list_keys),
            sorted(response.data["results"][0].keys()),
        )

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

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

    def test_get_list_with_filter_name(self):
        # name = student 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"name": "student 1"}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertNotIn(self.student2.id, ids)

        # name student X
        response = self.forced_authenticated_client.get(
            self.list_url, {"name": "student X"}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student1.id, ids)
        self.assertNotIn(self.student2.id, ids)

    def test_get_list_with_filter_added_by(self):
        # added_by = student 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"added_by": self.student1.added_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertNotIn(self.student2.id, ids)

        # added_by student X
        response = self.forced_authenticated_client.get(
            self.list_url, {"added_by": self.student2.added_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

    def test_get_list_with_filter_is_active(self):
        # is_active = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": True}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

        # is_active = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student1.id, ids)
        self.assertNotIn(self.student2.id, ids)

    def test_get_list_with_filter_visible_for_guest(self):
        # visible_for_guest = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"visible_for_guest": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

        # visible_for_guest = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"visible_for_guest": True}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student1.id, ids)
        self.assertNotIn(self.student2.id, ids)

    def test_get_list_success_with_filter_tag(self):
        # prepare data
        tag1 = TagFactory.create(name="name_1", slug="slug_1")
        tag2 = TagFactory.create(name="name_2", slug="slug_2")
        TaggedStudentFactory.create(content_object=self.student1, tag=tag1)
        TaggedStudentFactory.create(content_object=self.student1, tag=tag2)
        TaggedStudentFactory.create(content_object=self.student2, tag=tag2)

        # tag = tag1.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": tag1.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertNotIn(self.student2.id, ids)

        # tag = tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": tag2.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

        # tag = tag1.name, tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": "{},{}".format(tag1.name, tag2.name)},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

    def test_get_list_with_filter_caseload_only(self):
        # caseload_only = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"caseload_only": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

        # first: caseload_only = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"caseload_only": True}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.student1.id, ids)
        self.assertNotIn(self.student2.id, ids)

        # second: caseload_only = True
        UserStudentMappingFactory.create(
            user=self.normal_user,
            student=self.student1,
            added_by=self.manager_user,
        )
        UserStudentMappingFactory.create(
            user=self.normal_user,
            student=self.student2,
            added_by=self.manager_user,
        )

        response = self.forced_authenticated_client.get(
            self.list_url, {"caseload_only": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.student1.id, ids)
        self.assertIn(self.student2.id, ids)

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.student1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:students-detail", args=[-1])
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_success(self):
        data = {
            "first_name": "James Joseph",
            "last_name": "Tarkin",
            "nickname": "JT",
            "is_active": True,
            "visible_for_guest": False,
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.student1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_with_partial_detail(self):
        data = {"first_name": "James Joseph"}

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.student1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_delete_success(self):
        student3 = StudentFactory.create(nickname="student 3")

        response = self.forced_authenticated_client.delete(
            reverse("v1:students-detail", args=[student3.id])
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.forced_authenticated_client.get(
            reverse("v1:students-detail", args=[student3.id])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:students-detail", args=[-1])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_success(self):
        data = {
            "first_name": "James Joseph",
            "last_name": "Tarkin",
            "nickname": "JT",
            "is_active": True,
            "visible_for_guest": False,
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_create_fail(self):
        data = {
            "first_name": 1,
            "nickname": "JT",
            "is_active": True,
            "visible_for_guest": False,
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("last_name", response.data)

    def test_get_heads_up(self):
        response = self.forced_authenticated_client.get(self.heads_up_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([], response.data)

        episode = EpisodeFactory.create(
            student=self.student1, heads_up_json={"test": "hello"}
        )

        response = self.forced_authenticated_client.get(self.heads_up_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("hello", response.data[0]["test"])
        self.assertEqual(episode.date, response.data[0]["date"])

    def test_get_list_success_experimental_teacher(self):
        user = UserFactory(role=constants.Role.EXPERIMENTAL_TEACHER)
        client = self.get_authenticated_client(user)

        response = client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))
        self.assertEqual(0, len(response.data["results"]))

        # Add a new student
        student = StudentFactory.create(added_by=user)

        response = client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))
        self.assertEqual(1, len(response.data["results"]))
        self.assertEqual(student.id, response.data["results"][0]["id"])

    def test_get_detail_success_experimental_teacher(self):
        user = UserFactory(role=constants.Role.EXPERIMENTAL_TEACHER)
        client = self.get_authenticated_client(user)

        response = client.get(self.detail_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        # Add a new student
        student = StudentFactory.create(added_by=user)
        detail_url = reverse("v1:students-detail", args=[student.id])

        response = client.get(detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(student.id, response.data["id"])

    def test_get_list_with_check_number_of_tips(self):
        student1 = StudentFactory.create()
        student2 = StudentFactory.create()

        student_tip1 = StudentTipFactory.create(student=student1)
        student_tip1.created_at = timezone.localtime() - timezone.timedelta(
            days=1
        )
        student_tip1.save()

        student_tip2 = StudentTipFactory.create(student=student2)
        student_tip2.created_at = timezone.localtime() - timezone.timedelta(
            days=30
        )
        student_tip2.save()

        response = self.forced_authenticated_client.get(self.list_url)

        data = {}
        for item in response.data["results"]:
            student_id = item["id"]
            data[student_id] = item["number_of_tips"]

        self.assertEqual(data[student1.id], 1)
        self.assertEqual(data[student2.id], 0)

    @classmethod
    @mute_signals(signals.pre_save, signals.post_save)
    def create_student_notifications(cls):
        cls.content_types = ContentType.objects.get_for_models(
            Tip, Student, User
        )

        student_tip = StudentTipFactory.create(student=cls.student1)

        cls.student_tip_notification = Notification.objects.create(
            actor_object_id=student_tip.added_by_id,
            actor_content_type_id=cls.content_types[User].id,
            recipient=student_tip.student.added_by,
            action_object=student_tip.tip,
            target=cls.student1,
            level="info",
            timestamp=timezone.now() - timezone.timedelta(days=15),
        )

    def test_get_student_notifications_with_manager_user(self):
        response = self.authenticated_manager_client.get(
            self.student_notifications_url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(self.student_tip_notification.id, ids)

    def test_get_student_notifications_with_manager_user_and_filter_start_date(
        self,
    ):
        data_params = {
            "start_date": timezone.localtime() - timezone.timedelta(18)
        }
        response = self.authenticated_manager_client.get(
            self.student_notifications_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(self.student_tip_notification.id, ids)

    def test_get_student_notifications_with_manager_user_and_filter_end_date(
        self,
    ):
        data_params = {
            "end_date": timezone.localtime() - timezone.timedelta(18)
        }
        response = self.authenticated_manager_client.get(
            self.student_notifications_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertNotIn(self.student_tip_notification.id, ids)

    def test_get_student_notifications_with_manager_user_and_filter_content_type(
        self,
    ):
        # content_type = tip
        data_params = {"content_type_id": self.content_types[Tip].id}
        response = self.authenticated_manager_client.get(
            self.student_notifications_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(self.student_tip_notification.id, ids)

    def test_get_student_notifications_with_normal_user(self):
        response = self.forced_authenticated_client.get(
            self.student_notifications_url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(self.student_tip_notification.id, ids)

    def test_get_student_notifications_with_normal_user_and_filter_start_date(
        self,
    ):
        data_params = {
            "start_date": timezone.localtime() - timezone.timedelta(18)
        }
        response = self.forced_authenticated_client.get(
            self.student_notifications_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(self.student_tip_notification.id, ids)

    def test_get_student_notifications_with_normal_user_and_filter_end_date(
        self,
    ):
        data_params = {
            "end_date": timezone.localtime() - timezone.timedelta(18)
        }
        response = self.forced_authenticated_client.get(
            self.student_notifications_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertNotIn(self.student_tip_notification.id, ids)

    def test_get_student_notifications_with_normal_user_and_filter_content_type(
        self,
    ):
        # content_type = tip
        data_params = {"content_type_id": self.content_types[Tip].id}
        response = self.forced_authenticated_client.get(
            self.student_notifications_url, data=data_params
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.data]
        self.assertIn(self.student_tip_notification.id, ids)
