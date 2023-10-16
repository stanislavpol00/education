from django.core.cache import cache
from django.db import connection
from django.test.utils import override_settings

import constants
from main.models import User
from tests.base_test import BaseTestCase
from tests.factories import (
    OrganizationFactory,
    RoleAssignmentFactory,
    StudentTipFactory,
    TipFactory,
    TipRatingFactory,
    UserFactory,
    UserStudentMappingFactory,
)


class TestUser(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create()

    def test_create_user_success(self):
        user = User.objects.create_user(
            "email_user_1@gmail.com",
            "email_user_1",
            constants.Role.EDUCATOR_SHADOW,
            "password!@#123",
        )

        self.assertTrue(user.id >= 1)

    def test_create_user_fail_email(self):
        self.assertRaises(
            Exception,
            User.objects.create_user,
            None,
            "email_user_1",
            constants.Role.EDUCATOR_SHADOW,
            "password!@#123",
        )

    def test_create_user_fail_username(self):
        self.assertRaises(
            Exception,
            User.objects.create_user,
            "email_user_1@gmail.com",
            None,
            constants.Role.EDUCATOR_SHADOW,
            "password!@#123",
        )

    def test_create_superuser_success(self):
        user = User.objects.create_superuser(
            "email_user_1@gmail.com",
            "email_user_1",
            "password!@#123",
            constants.Role.EDUCATOR_SHADOW,
        )

        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.id >= 1)

    def test_mangers_success(self):
        managers = User.objects.managers()

        ids = managers.values_list("id", flat=True)
        self.assertIn(self.manager_user.id, ids)

    @override_settings(DEBUG=True)
    def test_cache_managers(self):
        cache.delete(constants.Cache.MANAGER_USERS_CACHE_KEY)

        # first call
        User.objects.managers()
        current_count = len(connection.queries)

        # second call
        User.objects.managers()
        new_count = len(connection.queries)
        self.assertEqual(current_count + 1, new_count)

    def test_to_dict(self):
        user_dicts = User.objects.to_dict([self.user.id])

        is_existed = self.user.id in user_dicts
        self.assertTrue(is_existed)

    def test_by_role(self):
        # check when role = None
        expected = User.objects.all()
        actual = User.objects.by_role()

        self.assertQuerysetEqual(actual, expected, ordered=False)

    def test_annotate_full_name(self):
        users = User.objects.all()
        expected = [
            "{} {}".format(user.first_name, user.last_name) for user in users
        ]

        annotated_users = User.objects.annotate_full_name()
        actual = [
            "{} {}".format(user.first_name, user.last_name)
            for user in annotated_users
        ]

        self.assertListEqual(actual, expected)

    def test_filter_by_params(self):
        # filter param = None
        expected = User.objects.all()
        for user in expected:
            user.full_name = "{} {}".format(user.first_name, user.last_name)

        actual = User.objects.filter_by_params()

        self.assertQuerysetEqual(actual, expected, ordered=False)

        # filter full_name and role
        user = UserFactory.create(
            first_name="test_filter_ACD",
            last_name="EDF",
            role=constants.Role.EDUCATOR_SHADOW,
        )
        filtered_users = User.objects.filter_by_params(
            full_name="test_filter_ACD E", role=constants.Role.EDUCATOR_SHADOW
        )
        ids = [user.id for user in filtered_users]

        self.assertEqual([user.id], ids)

    def test_annotate_tips_count(self):
        tip = TipFactory.create()
        TipRatingFactory.create(
            tip=tip,
            added_by=self.user,
            try_count=5,
        )
        student_tip = StudentTipFactory.create(tip=tip)
        UserStudentMappingFactory.create(
            user=self.user,
            student=student_tip.student,
            added_by=self.manager_user,
        )

        user = (
            User.objects.annotate_tips_count().filter(pk=self.user.id).first()
        )

        self.assertEqual(1, user.unique_tried_tips_count)
        self.assertEqual(5, user.tried_tips_total)
        self.assertEqual(1, user.assigned_tips_count)

    @override_settings(DEBUG=True)
    def test_by_username_or_email(self):
        count = len(connection.queries)
        # username
        user = User.objects.by_username_or_email(self.user.username)
        count1 = len(connection.queries)

        self.assertEqual(count + 1, count1)

        self.assertEqual(self.user.id, user.id)

        # email
        user = User.objects.by_username_or_email(self.user.email)
        count2 = len(connection.queries)

        self.assertEqual(count1 + 1, count2)

        self.assertEqual(self.user.id, user.id)

    def test_annotate_number_tip_rating_reminder(self):
        TipRatingFactory.create(
            clarity=0,
            relevance=0,
            uniqueness=0,
            read_count=0,
            added_by=self.user,
        )
        TipRatingFactory.create(
            clarity=0,
            relevance=0,
            uniqueness=1,
            read_count=1,
            added_by=self.user,
        )
        TipRatingFactory.create(
            clarity=0,
            relevance=0,
            uniqueness=0,
            read_count=1,
            added_by=self.user,
        )

        user = (
            User.objects.annotate_number_tip_rating_reminder()
            .filter(pk=self.user.id)
            .first()
        )

        self.assertEqual(user.number_of_tips, 1)

    def test_by_user_organization__for_superuser(self):
        # Prepare Data
        org1 = OrganizationFactory.create()
        org2 = OrganizationFactory.create()

        user1 = UserFactory.create()
        RoleAssignmentFactory.create(
            user=user1,
            organization=org1,
        )

        user2 = UserFactory.create()
        RoleAssignmentFactory.create(
            user=user2,
            organization=org2,
        )

        user3 = UserFactory.create()

        # Action 1: get users without organization_id
        queryset = User.objects.by_user_organization(self.super_user)

        # Assert for action 1
        self.assertIn(user1, queryset)
        self.assertIn(user2, queryset)
        self.assertIn(user3, queryset)

        # Action 2: get users with organization_id
        queryset = User.objects.by_user_organization(
            self.super_user, organization_id=org1.id
        )

        # Assert for action 2
        self.assertIn(user1, queryset)
        self.assertNotIn(user2, queryset)
        self.assertNotIn(user3, queryset)

    def test_by_user_organization__for_normal_user(self):
        # Prepare Data
        org1 = OrganizationFactory.create()
        org2 = OrganizationFactory.create()

        RoleAssignmentFactory.create(
            user=self.normal_user,
            organization=org1,
            group=self.admin_group,
        )

        RoleAssignmentFactory.create(
            user=self.normal_user,
            organization=org2,
            group=self.staff_group,
        )

        user1 = UserFactory.create()
        RoleAssignmentFactory.create(
            user=user1, organization=org1, group=self.admin_group
        )

        user2 = UserFactory.create()
        RoleAssignmentFactory.create(
            user=user2,
            organization=org1,
            group=self.staff_group,
        )

        user3 = UserFactory.create()
        RoleAssignmentFactory.create(
            user=user3,
            organization=org2,
            group=self.staff_group,
        )

        user4 = UserFactory.create()
        RoleAssignmentFactory.create(
            user=user4,
            organization=org2,
            group=self.dlp_group,
        )

        user5 = UserFactory.create()
        RoleAssignmentFactory.create(
            user=user5,
            organization=org2,
            group=self.guest_group,
        )

        user6 = UserFactory.create()

        # Action 1: get users without organization_id
        queryset = User.objects.by_user_organization(self.normal_user)

        # Assert for action 1
        self.assertFalse(queryset.exists())

        # Action 2: get users with org1
        queryset = User.objects.by_user_organization(
            self.normal_user, organization_id=org1.id
        )

        # Assert for action 2
        # Admin cannot see admin user
        self.assertNotIn(user1, queryset)
        # Admin can see staff user
        self.assertIn(user2, queryset)
        # Admin cannot see other organization
        self.assertNotIn(user3, queryset)
        self.assertNotIn(user4, queryset)
        self.assertNotIn(user5, queryset)
        # Admin cannot see user not assign to any organization
        self.assertNotIn(user6, queryset)

        # Action 3: get users with org2
        queryset = User.objects.by_user_organization(
            self.normal_user, organization_id=org2.id
        )

        # Assert for action 2
        # Staff cannot see other organization
        self.assertNotIn(user1, queryset)
        self.assertNotIn(user2, queryset)
        # Staff cannot see staff user
        self.assertNotIn(user3, queryset)
        # Staff can see dlp, staff user
        self.assertIn(user4, queryset)
        self.assertIn(user5, queryset)
        # Staff cannot see user not assign to any organization
        self.assertNotIn(user6, queryset)
