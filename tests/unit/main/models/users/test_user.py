import factory
from django.conf import settings
from django.contrib.auth.models import Group
from django.core import mail
from django.core.files.base import ContentFile
from django_rest_passwordreset.models import ResetPasswordToken

import constants
from tests.base_test import BaseTestCase
from tests.factories import (
    OrganizationFactory,
    RoleAssignmentFactory,
    UserFactory,
    UserStudentMappingFactory,
)


class TestUser(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user1 = UserFactory.create(is_superuser=True)
        cls.user2 = UserFactory.create(first_name="F", last_name="L")

    def test_get_full_name(self):
        self.assertEqual("F L", self.user2.get_full_name())

    def test_full_name(self):
        self.assertEqual("F L", self.user2.full_name)

    def test_is_staff(self):
        self.assertTrue(self.user1.is_staff)
        self.assertFalse(self.user2.is_staff)

    def test_is_role_guest_true(self):
        user = UserFactory.create(role=constants.Role.GUEST)

        self.assertTrue(user.is_role_guest)

    def test_is_role_guest_false(self):
        user = UserFactory.create(role=constants.Role.EDUCATOR_SHADOW)

        self.assertFalse(user.is_role_guest)

    def test_photo_url(self):
        content = ContentFile(
            factory.django.ImageField()._make_data(
                {"width": 1024, "height": 768}
            )
        )
        profile = self.user1.profile
        profile.photo.save("myphoto.jpg", content, save=True)
        profile.save()

        self.assertIn("media", self.user1.photo_url)

    def test_role_description(self):
        self.assertEqual("Educator Shadow", self.user2.role_description)

    def test_photo_width(self):
        content = ContentFile(
            factory.django.ImageField()._make_data(
                {"width": 1024, "height": 768}
            )
        )
        profile = self.user1.profile
        profile.photo.save("myphoto.jpg", content, save=True)
        profile.save()

        self.assertEqual(1024, self.user1.photo_width)

    def test_photo_height(self):
        content = ContentFile(
            factory.django.ImageField()._make_data(
                {"width": 1024, "height": 768}
            )
        )
        profile = self.user1.profile
        profile.photo.save("myphoto.jpg", content, save=True)
        profile.save()

        self.assertEqual(768, self.user1.photo_height)

    def test_is_role_experimental_teacher(self):
        user = UserFactory.create(role=constants.Role.EXPERIMENTAL_TEACHER)

        self.assertTrue(user.is_role_experimental_teacher)

    def test_assigned_students(self):
        user_student_1 = UserStudentMappingFactory.create(
            user=self.experimental_user,
            added_by=self.manager_user,
        )
        user_student_2 = UserStudentMappingFactory.create(
            user=self.experimental_user,
            added_by=self.manager_user,
        )

        expected_data = [user_student_1.student, user_student_2.student]

        actual_data = list(self.experimental_user.assigned_students)

        self.assertQuerysetEqual(actual_data, expected_data, ordered=False)

    def test_update_last_login(self):
        last_login = self.user1.last_login
        self.assertIsNone(last_login)

        self.user1.update_last_login()

        self.user1.refresh_from_db()
        new_last_login = self.user1.last_login

        self.assertIsNotNone(new_last_login)

    def test_get_password_reset_link(self):
        expected_link = "{}login/?reset-request-token={}".format(
            settings.WEB_URL, 123456
        )
        reset_password_token = ResetPasswordToken(key=123456)

        password_reset_link = self.user1.get_password_reset_link(
            reset_password_token
        )

        self.assertEqual(expected_link, password_reset_link)

    def test_send_registered_email(self):
        reset_password_token = ResetPasswordToken.objects.create(
            user=self.user1
        )

        self.user1.send_registered_email(reset_password_token)

        # check send email successfully
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "You have been registered at ORG!",
        )

    def test_role_assignments(self):
        user = UserFactory.create()
        role_assignments = RoleAssignmentFactory.create_batch(3, user=user)
        expect_result = [
            {
                "group": role_assignment.group.name,
                "organization": role_assignment.organization_id,
            }
            for role_assignment in role_assignments
        ]

        result = user.role_assignments

        self.assertEqual(expect_result, result)

    def test_organization_roles_mapping(self):
        user = UserFactory.create()
        role_assignments = RoleAssignmentFactory.create_batch(3, user=user)
        expect_result = {
            role_assignment.organization_id: role_assignment.group.name
            for role_assignment in role_assignments
        }

        result = user.organization_roles_mapping

        self.assertEqual(expect_result, result)

    def _test_check_organization_role(
        self, check_role_method_name, target_role
    ):
        user = UserFactory.create()
        organization = OrganizationFactory.create()

        role_assignments = []
        for group_name in constants.Group.ALL_ORGANIZATION_ROLES:
            group = Group.objects.get(name=group_name)
            role_assignments.append(
                RoleAssignmentFactory.create(user=user, group=group)
            )

        # user has not role
        self.assertFalse(user.is_organization_guest(organization.id))
        check_role_method = getattr(user, check_role_method_name)
        for role_assignment in role_assignments:
            # TODO: it currently failed.
            if role_assignment.group.name == target_role:
                self.assertTrue(
                    check_role_method(role_assignment.organization.id)
                )
            else:
                self.assertFalse(
                    check_role_method(role_assignment.organization.id)
                )

    def test_is_organization_guest(self):
        self._test_check_organization_role(
            "is_organization_guest", constants.Group.ORGANIZATION_GUEST
        )

    def test_is_organization_dlp(self):
        self._test_check_organization_role(
            "is_organization_dlp", constants.Group.ORGANIZATION_DLP
        )

    def test_is_organization_staff(self):
        self._test_check_organization_role(
            "is_organization_staff", constants.Group.ORGANIZATION_STAFF
        )

    def test_is_organization_admin(self):
        self._test_check_organization_role(
            "is_organization_admin", constants.Group.ORGANIZATION_ADMIN
        )

    def test_can_manage_organization_role(self):
        # Prepare
        user = UserFactory.create()
        organization = OrganizationFactory.create()
        group = Group.objects.get(name=constants.Group.ORGANIZATION_DLP)

        # User not assign to organization, then cannot manage any role
        self.assertFalse(
            user.can_manage_organization_role(
                organization.id, constants.Group.ORGANIZATION_ADMIN
            )
        )

        # assign user as organization's DLP
        del user.organization_roles_mapping
        del user.role_assignments
        RoleAssignmentFactory.create(
            user=user, organization=organization, group=group
        )

        # DLP role cannot manage GUEST role
        self.assertFalse(
            user.can_manage_organization_role(
                organization.id, constants.Group.ORGANIZATION_GUEST
            )
        )
        # DLP role cannot manage higher ordering roles
        for role in [
            constants.Group.ORGANIZATION_ADMIN,
            constants.Group.ORGANIZATION_STAFF,
            constants.Group.ORGANIZATION_DLP,
        ]:
            self.assertFalse(
                user.can_manage_organization_role(organization.id, role)
            )

        # make user become superuser. User can manage all roles
        user.is_superuser = True
        user.save()
        for role in constants.Group.ALL_ORGANIZATION_ROLES:
            self.assertTrue(
                user.can_manage_organization_role(organization.id, role)
            )
