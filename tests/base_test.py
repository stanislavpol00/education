import copy

from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property

import constants
from main.models import User

from .factories import UserFactory


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Prepare groups
        cls.admin_group, _ = Group.objects.get_or_create(
            name=constants.Group.ORGANIZATION_ADMIN
        )
        cls.staff_group, _ = Group.objects.get_or_create(
            name=constants.Group.ORGANIZATION_STAFF
        )
        cls.dlp_group, _ = Group.objects.get_or_create(
            name=constants.Group.ORGANIZATION_DLP
        )
        cls.guest_group, _ = Group.objects.get_or_create(
            name=constants.Group.ORGANIZATION_GUEST
        )

        cls.create_super_user()
        cls.create_admin_user()
        cls.create_normal_user()
        cls.create_manager_user()
        cls.create_experimental_user()
        cls.create_guest_user()

        cls.other_experimental_user = UserFactory.create(
            role=constants.Role.EXPERIMENTAL_TEACHER
        )

    @classmethod
    def create_super_user(cls):
        cls.super_username = "superuser123@gmail.com"
        cls.super_password = get_random_string(length=16)
        cls.super_email = "superuser123@gmail.com"
        cls.super_user, is_created = User.objects.get_or_create(
            username=cls.super_username,
            email=cls.super_email,
            is_superuser=True,
        )
        if is_created:
            cls.super_user.set_password(cls.super_password)
            cls.super_user.save()

    @classmethod
    def create_admin_user(cls):
        cls.admin_username = "admin123@gmail.com"
        cls.admin_password = get_random_string(length=16)
        cls.admin_email = "admin123@gmail.com"
        cls.admin_user, is_created = User.objects.get_or_create(
            username=cls.admin_username,
            email=cls.admin_email,
            role=constants.Role.ADMIN_USER,
        )
        if is_created:
            cls.admin_user.set_password(cls.admin_password)
            cls.admin_user.save()

    @classmethod
    def create_manager_user(cls):
        cls.manager_username = "manager123@gmail.com"
        cls.manager_password = get_random_string(length=16)
        cls.manager_email = "manager123@gmail.com"
        cls.manager_user, is_created = User.objects.get_or_create(
            username=cls.manager_username,
            email=cls.manager_email,
            role=constants.Role.MANAGER,
        )
        if is_created:
            cls.manager_user.set_password(cls.manager_password)
            cls.manager_user.save()

    @classmethod
    def create_experimental_user(cls):
        cls.experimental_username = "experimental123@gmail.com"
        cls.experimental_password = get_random_string(length=16)
        cls.experimental_email = "experimental123@gmail.com"
        cls.experimental_user, is_created = User.objects.get_or_create(
            username=cls.experimental_username,
            email=cls.experimental_email,
            role=constants.Role.EXPERIMENTAL_TEACHER,
        )
        if is_created:
            cls.experimental_user.set_password(cls.experimental_password)
            cls.experimental_user.save()

    @classmethod
    def create_normal_user(cls):
        cls.normal_username = "normal123@gmail.com"
        cls.normal_password = get_random_string(length=16)
        cls.normal_email = "normal123@gmail.com"
        cls.normal_user, is_created = User.objects.get_or_create(
            username=cls.normal_username, email=cls.normal_email
        )
        if is_created:
            cls.normal_user.set_password(cls.normal_password)
            cls.normal_user.save()

    @classmethod
    def create_guest_user(cls):
        cls.guest_username = "guest123@gmail.com"
        cls.guest_password = get_random_string(length=16)
        cls.guest_email = "guest123@gmail.com"
        cls.guest_user, is_created = User.objects.get_or_create(
            username=cls.guest_username,
            email=cls.guest_email,
            role=constants.Role.GUEST,
        )
        if is_created:
            cls.guest_user.set_password(cls.guest_password)
            cls.guest_user.save()

    @cached_property
    def super_user_client(self):
        client = Client()
        client.login(
            username=self.super_user.username, password=self.super_password
        )
        return client

    @cached_property
    def admin_client(self):
        client = Client()
        client.login(
            username=self.admin_user.username, password=self.admin_password
        )
        return client

    @cached_property
    def notifier_client(self):
        client = Client()
        client.login(
            username=self.notifier_user.username,
            password=self.notifier_password,
        )
        return client

    @cached_property
    def experimental_client(self):
        client = Client()
        client.login(
            username=self.experimental_user.username,
            password=self.experimental_password,
        )
        return client

    @cached_property
    def normal_client(self):
        client = Client()
        client.login(
            username=self.normal_user.username, password=self.normal_password
        )
        return client

    @cached_property
    def not_login_client(self):
        return Client()

    def make_deep_copy(self, data):
        return copy.deepcopy(data)

    def create_user(self):
        user = UserFactory.create()
        password = get_random_string(length=32)
        user.set_password(password)
        user.save()
        return {
            "user": user,
            "password": password,
        }
