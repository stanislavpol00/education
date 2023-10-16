from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.models import (
    ResetPasswordToken,
    clear_expired,
    get_password_reset_token_expiry_time,
)
from ipware import get_client_ip

import constants
from libs.cache import ActivityCache
from libs.messaging.email import Mailer

from ..managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        verbose_name=_("username"), max_length=255, unique=True
    )
    email = models.EmailField(
        verbose_name=_("email address"), max_length=255, unique=True
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.IntegerField(
        choices=constants.Role.CHOICES, default=constants.Role.EDUCATOR_SHADOW
    )
    is_team_lead = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)

    professional_goal = models.TextField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "role"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def full_name(self):
        return self.get_full_name()

    # for full_name annotate
    @full_name.setter
    def full_name(self, value):
        pass

    @property
    def is_role_experimental_teacher(self):
        return self.role == constants.Role.EXPERIMENTAL_TEACHER

    @property
    def is_dlp(self):
        return self.is_role_experimental_teacher

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_role_guest(self):
        return self.role == constants.Role.GUEST

    @property
    def is_role_admin(self):
        return self.role == constants.Role.ADMIN_USER

    @property
    def is_role_manager(self):
        return self.role == constants.Role.MANAGER

    @property
    def is_manager(self):
        return self.is_role_admin or self.is_role_manager

    # These methods are used for determining user's organization role
    @cached_property
    def role_assignments(self):
        return [
            {
                "group": role_assignment.group.name,
                "organization": role_assignment.organization_id,
            }
            for role_assignment in self.roleassignment_set.all()
        ]

    @cached_property
    def organization_roles_mapping(self):
        return {
            role_assignment["organization"]: role_assignment["group"]
            for role_assignment in self.role_assignments
        }

    @cached_property
    def organizations(self):
        return list(self.organization_roles_mapping.keys())

    def has_manage_organization_permission(self, organization_id):
        if self.is_superuser:
            return True

        if self.is_organization_admin(
            organization_id
        ) or self.is_organization_staff(organization_id):
            return True

        return False

    def can_manage_organization_role(self, organization_id, role):
        if self.is_superuser:
            return True

        if not self.has_manage_organization_permission(organization_id):
            return False

        user_role = self.organization_roles_mapping.get(organization_id)
        return (
            constants.Group.ORGANIZATION_ROLES_ORDERING.get(user_role) or 0
        ) > (constants.Group.ORGANIZATION_ROLES_ORDERING.get(role) or 0)

    def is_organization_guest(self, organization_id):
        role = self.organization_roles_mapping.get(organization_id)
        return role == constants.Group.ORGANIZATION_GUEST

    def is_organization_dlp(self, organization_id):
        role = self.organization_roles_mapping.get(organization_id)
        return role == constants.Group.ORGANIZATION_DLP

    def is_organization_staff(self, organization_id):
        role = self.organization_roles_mapping.get(organization_id)
        return role == constants.Group.ORGANIZATION_STAFF

    def is_organization_admin(self, organization_id):
        role = self.organization_roles_mapping.get(organization_id)
        return role == constants.Group.ORGANIZATION_ADMIN

    @property
    def photo_url(self):
        if self.profile.photo:
            return self.profile.photo.url

        return None

    @property
    def role_description(self):
        return self.get_role_display()

    @property
    def photo_width(self):
        return self.profile.photo_width

    @property
    def photo_height(self):
        return self.profile.photo_height

    @property
    def last_activity(self):
        return ActivityCache.get_last_activity_by_user(self.id)

    @property
    def assigned_students(self):
        from main.models import Student

        student_ids = self.experimental_user.values_list(
            "student_id", flat=True
        )
        students = Student.objects.filter(pk__in=student_ids)

        return students

    def get_activities(self, **kwargs):
        return ActivityCache.get_activities_by_user(self.id, **kwargs)

    def can_modify(self, user):
        return user.is_manager or self.id == user.id

    @property
    def tips_tried(self):
        from main.models import TipRating

        return TipRating.objects.get_tips_tried(self)

    def update_last_login(self):
        self.last_login = timezone.localtime()
        self.save()

    def update_access_info_cache(self, ip):
        """In order to reduce number of IpLogging records,
        we store the count and last_time in cache,
        and use it to determine that we should create record or not.

        We will only create records if:
        - User first logged in, or no access_info cache exists.
        - The count greater than the config value
        - The current access_time greater than the last one from config days or more.
        """
        now = timezone.now()
        username = self.get_username()
        cache_key = constants.Cache.ACCESS_LOG_CACHE_KEY.format(
            ip=ip,
            username=username,
        )
        access_info = cache.get(
            cache_key,
            default={
                "count": 0,
                "last_time": None,
            },
        )

        shoud_update_log = False
        if (
            access_info["count"] == 0
            or access_info["count"] >= settings.CACHE_ACCESS_LOG_MAX_COUNT
        ):
            shoud_update_log = True
        if (
            access_info["last_time"]
            and (now - access_info["last_time"]).days
            > settings.CACHE_ACCESS_LOG_MAX_DAYS
        ):
            shoud_update_log = True

        if shoud_update_log:
            access_info["count"] = 0

        access_info["count"] += 1
        access_info["last_time"] = now

        cache.set(
            cache_key,
            access_info,
            timeout=60 * 60 * 24 * 30,  # default to 30 days
        )

        return shoud_update_log

    def send_registered_email(self, reset_password_token):
        password_reset_link = self.get_password_reset_link(
            reset_password_token
        )

        Mailer.send_html_mail(
            subject=_("You have been registered at ORG!"),
            to_email=self.email,
            template_name="user_register.html",
            context={
                "password_reset_link": password_reset_link,
            },
        )

    def create_reset_password_token(self, request):
        # before we continue, delete all existing expired tokens
        # datetime.now minus expiry hours
        now_minus_expiry_time = timezone.now() - timezone.timedelta(
            hours=get_password_reset_token_expiry_time()
        )

        # delete all tokens where created_at < now - 24 hours
        clear_expired(now_minus_expiry_time)

        ip_address, _ = get_client_ip(request)

        reset_password_token = ResetPasswordToken.objects.create(
            user=self,
            ip_address=ip_address,
        )

        return reset_password_token

    def get_password_reset_link(self, reset_password_token):
        return "{}login/?reset-request-token={}".format(
            settings.WEB_URL, reset_password_token.key
        )
