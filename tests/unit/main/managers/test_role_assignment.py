from django.contrib.auth.models import Group
from django.utils.translation import gettext as _
from rest_framework import serializers

import constants
from main.models import RoleAssignment
from tests.base_test import BaseTestCase
from tests.factories import OrganizationFactory, RoleAssignmentFactory


class TestRoleAssignmentQuerySet(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.admin_group = Group.objects.get(
            name=constants.Group.ORGANIZATION_ADMIN
        )
        cls.staff_group = Group.objects.get(
            name=constants.Group.ORGANIZATION_STAFF
        )
        cls.dlp_group = Group.objects.get(
            name=constants.Group.ORGANIZATION_DLP
        )
        cls.guest_group = Group.objects.get(
            name=constants.Group.ORGANIZATION_GUEST
        )
        cls.organization1 = OrganizationFactory.create()
        cls.organization2 = OrganizationFactory.create()
        RoleAssignmentFactory.create(
            organization=cls.organization1,
            user=cls.admin_user,
            group=cls.staff_group,
        )
        RoleAssignmentFactory.create(
            organization=cls.organization2,
            user=cls.admin_user,
            group=cls.admin_group,
        )
        RoleAssignmentFactory.create(
            organization=cls.organization2,
            user=cls.guest_user,
            group=cls.guest_group,
        )

    def test_create_or_update_for_user_no_permission(self):
        with self.assertRaises(serializers.ValidationError) as ex:
            RoleAssignment.objects.create_or_update_for_user(
                user=self.guest_user,
                by_user=self.normal_user,
                role_assignments_data=[
                    {
                        "organization": self.organization1,
                        "group_name": self.dlp_group.name,
                        "group": self.dlp_group,
                    },
                    {
                        "organization": self.organization2,
                        "group_name": self.guest_group.name,
                        "group": self.guest_group,
                    },
                ],
            )

        self.assertIn(
            _(
                "Cannot creating or updating user's roles, "
                "dues to have no approviate permissions "
                "in these organization: {}"
            ).format(
                ",".join(
                    [str(self.organization1.id), str(self.organization2.id)]
                )
            ),
            ex.exception.detail,
        )

    def test_create_or_update_for_user_success(self):
        old_count = RoleAssignment.objects.count()

        RoleAssignment.objects.create_or_update_for_user(
            user=self.guest_user,
            by_user=self.admin_user,
            role_assignments_data=[
                {
                    "organization": self.organization1,
                    "group_name": self.dlp_group.name,
                    "group": self.dlp_group,
                },
                {
                    "organization": self.organization2,
                    "group_name": self.guest_group.name,
                    "group": self.guest_group,
                },
            ],
        )

        new_count = RoleAssignment.objects.count()

        self.assertEqual(new_count - old_count, 1)
        self.assertTrue(
            RoleAssignment.objects.filter(
                user=self.guest_user,
                organization=self.organization1,
                group=self.dlp_group,
            ).exists()
        )
        self.assertTrue(
            RoleAssignment.objects.filter(
                user=self.guest_user,
                organization=self.organization2,
                group=self.guest_group,
            ).exists()
        )
