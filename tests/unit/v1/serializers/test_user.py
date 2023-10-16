from django.test import TestCase

import constants
from tests.base_test import BaseTestCase
from tests.factories import UserFactory, UserStudentMappingFactory
from v1.serializers import UserChangeSerializer, UserSerializer


class TestUserSerializer(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create()
        cls.user_student1 = UserStudentMappingFactory.create(
            user=cls.user,
            added_by=cls.manager_user,
        )
        cls.user_student2 = UserStudentMappingFactory.create(
            user=cls.user,
            added_by=cls.manager_user,
        )

        cls.serializer = UserSerializer(cls.user)

        cls.expected_keys = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "username",
            "email",
            "date_joined",
            "is_staff",
            "role",
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
            "role_assignments",
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

    def test_to_representation_check_keys(self):
        self.assertListEqual(self.expected_keys, [*self.serializer.data])

    def test_to_representation_assigned_students(self):
        students = self.serializer.data["assigned_students"]

        assigned_student_keys = list(
            set().union(*(student.keys() for student in students))
        )
        self.assertEqual(
            sorted(assigned_student_keys), sorted(self.assigned_student_keys)
        )

        student_ids = [student["id"] for student in students]
        self.assertListEqual(
            [self.user_student1.student.id, self.user_student2.student.id],
            student_ids,
        )

    def test_to_representation_assigned_students_empty(self):
        user_has_not_students = UserFactory.build()
        serializer = UserSerializer(user_has_not_students)
        students = serializer["assigned_students"].value

        self.assertEqual(students, [])


class TestUserChangeSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create()

        cls.admin_user = UserFactory.create(role=constants.Role.ADMIN_USER)

        cls.normal_user = UserFactory.create(role=constants.Role.GUEST)

        cls.expected_keys = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "usertype",
            "professional_goal",
            "role_assignments",
        ]

        cls.validated_data = {
            "email": "new_email@education.com",
            "first_name": "first_name",
            "last_name": "last_name",
            "is_active": True,
            "role": 1,
            "usertype": constants.UserType.EDUCATOR_SHADOW,
            "professional_goal": "professional goal",
        }

    def test_validate_success(self):
        serializer = UserChangeSerializer(
            data=self.validated_data,
            instance=self.user,
            context={
                "request": type(
                    "Request", (object,), {"user": self.admin_user}
                )
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_to_representation_check_keys(self):
        serializer = UserChangeSerializer(
            data=self.validated_data,
            instance=self.user,
            context={
                "request": type(
                    "Request", (object,), {"user": self.admin_user}
                )
            },
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            sorted(self.expected_keys), sorted([*serializer.data])
        )

    def test_validate_fail_with_email(self):
        invalidated_data = {"email": "invalid_email"}

        serializer = UserChangeSerializer(
            data=invalidated_data,
            instance=self.user,
            context={
                "request": type(
                    "Request", (object,), {"user": self.admin_user}
                )
            },
        )
        serializer.is_valid()
        self.assertIn(
            "Enter a valid email address.", serializer.errors["email"]
        )

    def test_validate_fail_with_role(self):
        invalidated_data = {"role": 999}

        serializer = UserChangeSerializer(
            data=invalidated_data,
            instance=self.user,
            context={
                "request": type(
                    "Request", (object,), {"user": self.admin_user}
                )
            },
        )
        serializer.is_valid()
        self.assertIn(
            '"999" is not a valid choice.', serializer.errors["role"]
        )

    def test_validate_fail_with_role_and_normal_user(self):
        invalidated_data = {"role": constants.Role.ADMIN_USER}

        serializer = UserChangeSerializer(
            data=invalidated_data,
            instance=self.user,
            context={
                "request": type(
                    "Request", (object,), {"user": self.normal_user}
                )
            },
        )
        self.assertFalse(serializer.is_valid())

    def test_validate_fail_with_is_active_and_normal_user(self):
        invalidated_data = {"is_active": True}

        serializer = UserChangeSerializer(
            data=invalidated_data,
            instance=self.user,
            context={
                "request": type(
                    "Request", (object,), {"user": self.normal_user}
                )
            },
        )
        self.assertFalse(serializer.is_valid())
