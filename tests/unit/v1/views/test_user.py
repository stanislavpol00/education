import io
from unittest.mock import patch

from django.contrib.auth import authenticate
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework_simplejwt.state import token_backend

import constants
from main.models import UserStudentMapping
from main.querysets import RoleAssignmentQuerySet
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    StudentFactory,
    StudentTipFactory,
    TipFactory,
    TipRatingFactory,
    UserFactory,
    UserStudentMappingFactory,
)


class TestUserAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:users-list")

        cls.user1 = UserFactory.create(
            username="testusername1",
            email="testusername1@gmail.com",
            first_name="first_name 1",
            last_name="last_name 1",
            role=constants.Role.GUEST,
        )
        cls.user1.date_joined = timezone.localtime() - timezone.timedelta(
            days=1
        )
        cls.user1.save()

        cls.user2 = UserFactory.create(
            username="testusername2",
            email="testusername2@gmail.com",
            first_name="first_name 2",
            last_name="last_name 2",
            role=constants.Role.EDUCATOR_SHADOW,
        )

        cls.detail_url = reverse("v1:users-detail", args=[cls.user1.id])
        cls.jwt_url = reverse("v1:users-jwt", args=[cls.user1.id])
        cls.assigned_student_url = reverse(
            "v1:users-assign-students", args=[cls.user1.id]
        )
        cls.unassigned_student_url = reverse(
            "v1:users-unassign-students", args=[cls.user1.id]
        )
        cls.upload_photo_url = reverse(
            "v1:users-upload-photo", args=[cls.normal_user.id]
        )

        cls.expected_detail_keys = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "username",
            "email",
            "date_joined",
            "is_staff",
            "role",
            "role_assignments",
            "role_description",
            "photo_url",
            "photo_width",
            "photo_height",
            "is_team_lead",
            "assigned_students",
            "is_active",
            "unique_tried_tips_count",
            "tried_tips_total",
            "assigned_tips_count",
            "professional_goal",
        ]

        cls.assigned_student_keys = [
            "id",
            "first_name",
            "last_name",
            "nickname",
            "is_active",
            "image",
            "visible_for_guest",
            "created_at",
            "updated_at",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)

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

    def test_get_list_with_filter_username(self):
        # username = user 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"username": self.user1.username}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.user1.id, ids)
        self.assertNotIn(self.user2.id, ids)

        # username user 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"username": self.user2.username}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)

    def test_get_list_with_filter_email(self):
        # email = user 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"email": self.user1.email}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.user1.id, ids)
        self.assertNotIn(self.user2.id, ids)

        # email user 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"email": self.user2.email}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)

    def test_get_list_with_filter_full_name(self):
        # full_name = user 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"full_name": self.user1.full_name}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.user1.id, ids)
        self.assertNotIn(self.user2.id, ids)

        # full_name user 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"full_name": self.user2.full_name}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)

    def test_get_list_with_filter_is_active(self):
        # is_active = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": True}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)

        # is_active = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.user1.id, ids)
        self.assertNotIn(self.user2.id, ids)

    def test_get_list_with_filter_is_team_lead(self):
        # is_team_lead = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_team_lead": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)

        # is_team_lead = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_team_lead": True}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.user1.id, ids)
        self.assertNotIn(self.user2.id, ids)

    def test_get_list_with_filter_role(self):
        # role is from user 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"role": self.user1.role}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.user1.id, ids)
        self.assertNotIn(self.user2.id, ids)

        # role is from user 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"role": self.user2.role}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.user1.id, ids)
        self.assertIn(self.user2.id, ids)

    def test_get_list_with_ordering_first_name(self):
        # only filter user1 and user2, order by first_name ascending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "first_name"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user1.id, ids[0])
        self.assertEqual(self.user2.id, ids[1])

        # only filter user1 and user2, order by first_name descending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "-first_name"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user2.id, ids[0])
        self.assertEqual(self.user1.id, ids[1])

    def test_get_list_with_ordering_last_name(self):
        # only filter user1 and user2, order by last_name ascending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "last_name"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user1.id, ids[0])
        self.assertEqual(self.user2.id, ids[1])

        # only filter user1 and user2, order by last_name descending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "-last_name"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user2.id, ids[0])
        self.assertEqual(self.user1.id, ids[1])

    def test_get_list_with_ordering_full_name(self):
        # only filter user1 and user2, order by full_name ascending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "full_name"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user1.id, ids[0])
        self.assertEqual(self.user2.id, ids[1])

        # only filter user1 and user2, order by full_name descending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "-full_name"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user2.id, ids[0])
        self.assertEqual(self.user1.id, ids[1])

    def test_get_list_with_ordering_date_joined(self):
        # only filter user1 and user2, order by date_joined ascending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "date_joined"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user1.id, ids[0])
        self.assertEqual(self.user2.id, ids[1])

        # only filter user1 and user2, order by date_joined descending
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"username": "testusername", "ordering": "-date_joined"},
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(self.user2.id, ids[0])
        self.assertEqual(self.user1.id, ids[1])

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.user1.id, response.data["id"])

    def test_get_detail_success_with_check_tips_count(self):
        tip1 = TipFactory.create()
        tip2 = TipFactory.create()

        student1 = StudentFactory.create()
        student2 = StudentFactory.create()

        UserStudentMappingFactory.create(
            user=self.normal_user,
            student=student1,
            added_by=self.manager_user,
        )
        UserStudentMappingFactory.create(
            user=self.normal_user,
            student=student2,
            added_by=self.manager_user,
        )

        StudentTipFactory.create(tip=tip1, student=student1)
        StudentTipFactory.create(tip=tip2, student=student1)
        StudentTipFactory.create(tip=tip2, student=student2)

        TipRatingFactory.create(
            added_by=self.normal_user, tip=tip1, try_count=4
        )

        TipRatingFactory.create(
            added_by=self.normal_user, tip=tip2, try_count=0
        )

        detail_url = reverse("v1:users-detail", args=[self.normal_user.id])
        response = self.forced_authenticated_client.get(detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.normal_user.id, response.data["id"])
        self.assertEqual(response.data["unique_tried_tips_count"], 1)
        self.assertEqual(response.data["tried_tips_total"], 4)
        self.assertEqual(response.data["assigned_tips_count"], 2)

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:users-detail", args=[-1])
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(self.detail_url)

        self.assertEqual(
            status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code
        )

    @patch.object(RoleAssignmentQuerySet, "create_default")
    def test_create_success(self, mock_create_default):
        expected_keys = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_assignments",
            "password",
        ]

        data = {
            "username": "test_user_123",
            "email": "test@education.com",
            "first_name": "ABC",
            "last_name": "DEF",
            "role": constants.Role.EXPERIMENTAL_TEACHER,
        }

        response = self.authenticated_manager_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        user = authenticate(
            username="test_user_123", password=response.data["password"]
        )
        self.assertIsNotNone(user)

        # check send email successfully
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "You have been registered at ORG!",
        )

        # check confirm reset password successfully
        old_password = response.data["password"]

        client = self.get_main_client()

        body = mail.outbox[0].body
        token = body[body.index("token=") + 6 : body.index("token=") + 12]

        data = {"token": token, "password": "new_password"}

        response = client.post(
            reverse("drf-password-reset:reset-password-confirm"),
            data,
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        user.refresh_from_db()
        self.assertFalse(user.check_password(old_password))
        self.assertTrue(user.check_password("new_password"))

        mock_create_default.assert_called_once_with(user)

    def test_create_fail_with_duplicate_username(self):
        data = {
            "username": self.normal_username,
            "email": "test@education.com",
            "first_name": "ABC",
            "last_name": "DEF",
            "role": constants.Role.EXPERIMENTAL_TEACHER,
        }

        response = self.authenticated_manager_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn("username", response.data)

    def test_create_fail_with_duplicate_email(self):
        data = {
            "username": "test_user_123",
            "email": self.normal_email,
            "first_name": "ABC",
            "last_name": "DEF",
            "role": constants.Role.EXPERIMENTAL_TEACHER,
        }

        response = self.authenticated_manager_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn("email", response.data)

    def test_create_fail_with_check_role(self):
        data = {
            "username": "test_user_123",
            "email": "test@education.com",
            "first_name": "ABC",
            "last_name": "DEF",
            "role": constants.Role.MANAGER,
        }

        response = self.authenticated_manager_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn("role", response.data)

    def test_create_fail_with_check_permission(self):
        data = {}

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_assign_students_success(self):
        student1 = StudentFactory.create(nickname="student1")
        student2 = StudentFactory.create(nickname="student2")
        old_count = UserStudentMapping.objects.filter(
            user_id=self.user1.id
        ).count()

        data = {"students": [student1.id, student2.id]}
        response = self.authenticated_manager_client.post(
            self.assigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        current_count = UserStudentMapping.objects.filter(
            user_id=self.user1.id
        ).count()
        self.assertEqual(old_count + 2, current_count)

        response = self.authenticated_manager_client.post(
            self.assigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_count = UserStudentMapping.objects.filter(
            user_id=self.user1.id
        ).count()
        self.assertEqual(current_count, new_count)

    def test_assign_students_fail_with_students_not_exists(self):
        data = {
            # students not exists
            "students": [1221, 2121]
        }
        response = self.authenticated_manager_client.post(
            self.assigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_students_fail_with_user_not_found(self):
        user_id_not_found = 9999121
        student1 = StudentFactory.create(nickname="student1")
        data = {"students": [student1.id]}
        assigned_student_url = reverse(
            "v1:users-assign-students", args=[user_id_not_found]
        )

        response = self.authenticated_manager_client.post(
            assigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_assign_students_fail_with_check_permission(self):
        student1 = StudentFactory.create(nickname="student1")
        student2 = StudentFactory.create(nickname="student2")
        data = {
            # students not exists
            "students": [student1.id, student2.id]
        }
        response = self.forced_authenticated_client.post(
            self.assigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_detail_with_check_assigned_students(self):
        user_student1 = UserStudentMappingFactory.create(
            user=self.user1,
            added_by=self.manager_user,
        )
        user_student2 = UserStudentMappingFactory.create(
            user=self.user1,
            added_by=self.manager_user,
        )

        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        students = response.data["assigned_students"]

        student_keys = list(
            set().union(*(student.keys() for student in students))
        )
        self.assertEqual(
            sorted(student_keys), sorted(self.assigned_student_keys)
        )

        student_ids = [student["id"] for student in students]
        self.assertEqual(len(student_ids), 2)
        self.assertEqual(
            sorted([user_student1.student.id, user_student2.student.id]),
            sorted(student_ids),
        )

    def test_get_detail_with_check_assigned_students_empty(self):
        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        students = response.data["assigned_students"]

        self.assertEqual(students, [])

    @patch.object(RoleAssignmentQuerySet, "create_default")
    def test_update_with_full_detail_success_and_manager_user(
        self, mock_create_default
    ):
        data = {
            "email": "email@education.com",
            "first_name": "ABC",
            "last_name": "DEF",
            "is_active": True,
            "role": 3,
            "usertype": "PARENT",
        }

        response = self.authenticated_manager_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.user1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        mock_create_default.assert_called_once_with(self.user1)

    @patch.object(RoleAssignmentQuerySet, "create_default")
    def test_update_with_full_detail_success_and_owner_update(
        self, mock_create_default
    ):
        data = {
            "email": "email@education.com",
            "first_name": "ABC",
            "last_name": "DEF",
            "usertype": "PARENT",
        }

        detail_url = reverse("v1:users-detail", args=[self.normal_user.id])

        response = self.forced_authenticated_client.put(
            detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.normal_user.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        mock_create_default.assert_called_once_with(self.normal_user)

    def test_update_with_full_detail_fail_and_manager_user(self):
        data = {
            "email": "email@ORG",
            "first_name": "ABC",
            "last_name": "DEF",
            "is_active": True,
            "role": 999,
            "usertype": "PARENTTTT",
        }

        response = self.authenticated_manager_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("usertype", response.data)

    def test_update_with_full_detail_fail_with_owner_update(self):
        data = {
            "email": "emaieducationcom",
            "first_name": "ABC",
            "last_name": "DEF",
            "is_active": True,
            "role": 999,
            "usertype": "PARENTTT",
        }

        detail_url = reverse("v1:users-detail", args=[self.normal_user.id])

        response = self.forced_authenticated_client.put(
            detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("usertype", response.data)

    @patch.object(RoleAssignmentQuerySet, "create_default")
    def test_update_with_partial_detail_and_manager_user(
        self, mock_create_default
    ):
        data = {
            "email": "email@education.com",
            "is_active": True,
            "role": 3,
            "usertype": "PARENT",
            "professional_goal": "updated professional_goal",
        }

        response = self.authenticated_manager_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.user1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        mock_create_default.assert_called_once_with(self.user1)

    @patch.object(RoleAssignmentQuerySet, "create_default")
    def test_update_with_partial_detail_and_owner_manager_user_update_role(
        self, mock_create_default
    ):
        data = {"role": constants.Role.EXPERIMENTAL_TEACHER}

        detail_url = reverse("v1:users-detail", args=[self.manager_user.id])
        response = self.authenticated_manager_client.patch(
            detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.manager_user.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        mock_create_default.assert_called_once_with(self.manager_user)

    @patch.object(RoleAssignmentQuerySet, "create_default")
    def test_update_with_partial_detail_and_owner_user(
        self, mock_create_default
    ):
        data = {"email": "email@education.com"}

        detail_url = reverse("v1:users-detail", args=[self.normal_user.id])

        response = self.forced_authenticated_client.put(
            detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.normal_user.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        mock_create_default.assert_called_once_with(self.normal_user)

    def test_update_with_partial_detail_fail_and_manager_user(self):
        data = {"email": "email@learcom", "role": 999, "usertype": "PARENTTTT"}

        response = self.authenticated_manager_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("email", response.data)
        self.assertIn("role", response.data)
        self.assertIn("usertype", response.data)

    def test_update_with_partial_detail_fail_and_owner_user(self):
        data = {"role": 1, "is_active": False}

        detail_url = reverse("v1:users-detail", args=[self.normal_user.id])

        response = self.forced_authenticated_client.patch(
            detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn(
            "You do not allow update these fields",
            response.data["non_field_errors"],
        )

    def test_update_fail_with_manager_update_role_of_another_manager(self):
        data = {"role": constants.Role.EXPERIMENTAL_TEACHER}

        detail_url = reverse("v1:users-detail", args=[self.manager_user.id])
        response = self.authenticated_admin_client.patch(
            detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn("You do not allow update these fields", response.data)

    def test_update_fail_with_normal_user_update_for_other_user(self):
        data = {"role": 1, "is_active": False}

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.seek(0)
        return file

    def test_upload_photo_success_with_manager(self):
        self.assertIsNone(self.user1.profile.photo.name)

        # set up form data
        photo = self.generate_photo_file()
        photo_file = SimpleUploadedFile("test.png", photo.getvalue())
        data = {"file": photo_file}

        response = self.authenticated_manager_client.patch(
            self.upload_photo_url, data=data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertIsNotNone(self.user1.profile.photo.name)

    def test_upload_photo_success_with_owner(self):
        self.assertIsNone(self.user1.profile.photo.name)

        photo = self.generate_photo_file()
        photo_file = SimpleUploadedFile("test.png", photo.getvalue())
        data = {"file": photo_file}

        response = self.forced_authenticated_client.patch(
            self.upload_photo_url, data=data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertIsNotNone(self.user1.profile.photo.name)

    def test_upload_photo_fail_with_invalid_file_and_manger_user(self):
        self.assertIsNone(self.user1.profile.photo.name)

        invalid_file = SimpleUploadedFile(
            "file.txt", b"abc", content_type="text/plain"
        )
        data = {"file": invalid_file}

        response = self.authenticated_manager_client.patch(
            self.upload_photo_url, data=data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Unsupported image type")

    def test_upload_photo_fail_with_invalid_file_and_normal_user(self):
        self.assertIsNone(self.user1.profile.photo.name)

        invalid_file = SimpleUploadedFile(
            "file.txt", b"abc", content_type="text/plain"
        )
        data = {"file": invalid_file}

        response = self.forced_authenticated_client.patch(
            self.upload_photo_url, data=data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Unsupported image type")

    def test_upload_photo_fail_with_normal_user_update_for_other_user(self):
        self.assertIsNone(self.user1.profile.photo.name)

        invalid_file = SimpleUploadedFile(
            "file.txt", b"abc", content_type="text/plain"
        )
        data = {"file": invalid_file}
        upload_photo_url = reverse(
            "v1:users-upload-photo", args=[self.user1.id]
        )

        response = self.forced_authenticated_client.patch(
            upload_photo_url, data=data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unassign_students_success(self):
        student1 = StudentFactory.create(nickname="student1")
        student2 = StudentFactory.create(nickname="student2")

        UserStudentMappingFactory.create(
            student=student1,
            user=self.user1,
            added_by=self.manager_user,
        )
        UserStudentMappingFactory.create(
            student=student2,
            user=self.user1,
            added_by=self.manager_user,
        )

        old_count = UserStudentMapping.objects.filter(
            user_id=self.user1.id
        ).count()

        data = {"students": [student1.id, student2.id]}
        response = self.authenticated_manager_client.post(
            self.unassigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        current_count = UserStudentMapping.objects.filter(
            user_id=self.user1.id
        ).count()
        self.assertEqual(old_count - 2, current_count)

        response = self.authenticated_manager_client.post(
            self.unassigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_count = UserStudentMapping.objects.filter(
            user_id=self.user1.id
        ).count()
        self.assertEqual(current_count, new_count)

    def test_unassign_students_fail_with_students_not_exists(self):
        data = {
            # students not exists
            "students": [-1, -2]
        }
        response = self.authenticated_manager_client.post(
            self.unassigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unassign_students_fail_with_user_not_found(self):
        user_id_not_found = 9999121
        student1 = StudentFactory.create(nickname="student1")
        data = {"students": [student1.id]}
        unassigned_student_url = reverse(
            "v1:users-unassign-students", args=[user_id_not_found]
        )

        response = self.authenticated_manager_client.post(
            unassigned_student_url, data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(
        TEMPORARY_JWT_EXPIRATION_DELTA=timezone.timedelta(minutes=10)
    )
    def test_jwt_success(self):
        time1 = timezone.now() + timezone.timedelta(minutes=10)

        response = self.authenticated_manager_client.post(
            self.jwt_url, format="json"
        )

        time2 = timezone.now() + timezone.timedelta(minutes=10)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = token_backend.decode(response.data["token"])

        self.assertEqual(payload["username"], self.user1.username)
        self.assertGreater(time1.timestamp(), payload["exp"])
        self.assertLess(payload["exp"], time2.timestamp())

        # check use token
        client = self.get_main_client()
        client.credentials(
            HTTP_AUTHORIZATION="JWT {}".format(response.data["token"])
        )

        url = reverse("api-auth:rest_user_details")

        response = client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user1.id)

    def test_jwt_fail_with_check_permission(self):
        response = self.forced_authenticated_client.post(
            self.jwt_url, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
