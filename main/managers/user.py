from django.contrib.auth.base_user import BaseUserManager
from django.core.cache import cache
from django.db.models import Count, Exists, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Concat
from django.utils.translation import gettext_lazy as _

import constants
from main.models import RoleAssignment


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        role,
        password=None,
    ):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError(_("Users must have an email address"))

        if not username:
            raise ValueError(_("Users must have an username"))
        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, role):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email, password=password, username=username, role=role
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def by_role(self, role=None):
        queryset = self.get_queryset()

        if role:
            queryset = queryset.filter(role=role)

        return queryset

    def managers(self):
        key_name = constants.Cache.MANAGER_USERS_CACHE_KEY
        value = cache.get(key_name)

        if value:
            return value

        queryset = self.get_queryset().filter(role__in=constants.Role.MANAGERS)

        cache.set(key_name, queryset, timeout=constants.Cache.TIMEOUT_A_DAY)

        return queryset

    def annotate_full_name(self):
        queryset = self.get_queryset().annotate(
            full_name=Concat("first_name", Value(" "), "last_name")
        )

        return queryset

    def to_dict(self, user_ids):
        queryset = self.get_queryset().filter(id__in=user_ids)

        users = {}
        for user in queryset:
            users[user.id] = user
        return users

    def filter_by_params(self, **kwargs):
        queryset = self.annotate_full_name()

        if kwargs.get("full_name"):
            queryset = queryset.filter(
                full_name__icontains=kwargs["full_name"]
            )

        if kwargs.get("role"):
            queryset = queryset.filter(role=kwargs["role"])

        return queryset

    def annotate_tips_count(self):
        from main.models import TipRating

        tip_ratings = (
            TipRating.objects.filter(
                added_by_id=OuterRef("pk"), try_count__gt=0
            )
            .values("added_by_id")
            .annotate(
                unique_tried_tips_count=Count("tip_id"),
                tried_tips_total=Sum("try_count"),
            )
        )

        queryset = self.get_queryset().annotate(
            unique_tried_tips_count=Coalesce(
                tip_ratings.values("unique_tried_tips_count")[:1], 0
            ),
            tried_tips_total=Coalesce(
                tip_ratings.values("tried_tips_total")[:1], 0
            ),
            assigned_tips_count=Count(
                "experimental_user__student__studenttip__tip_id", distinct=True
            ),
        )

        return queryset

    def by_username_or_email(self, username_or_email):
        return (
            self.get_queryset()
            .filter(Q(username=username_or_email) | Q(email=username_or_email))
            .first()
        )

    def annotate_number_tip_rating_reminder(self):
        from main.models import TipRating

        tip_ratings_reminder = (
            TipRating.objects.get_read_but_not_rated_tip_ratings()
            .filter(added_by_id=OuterRef("pk"))
            .values("added_by_id")
            .annotate(number_of_tips=Count("id"))
            .values_list("number_of_tips")
        )

        return (
            self.filter(
                role__in=constants.Role.EDUCATORS + constants.Role.MANAGERS
            )
            .annotate(
                number_of_tips=Coalesce(Subquery(tip_ratings_reminder), 0)
            )
            .filter(number_of_tips__gt=0)
        )

    def by_user_organization(self, user, organization_id=None, queryset=None):
        queryset = queryset or self.get_queryset()

        if not organization_id:
            if user.is_superuser:
                return queryset
            else:
                return queryset.none()

        role_filters = {
            "user": OuterRef("id"),
            "organization_id": organization_id,
        }

        role = user.organization_roles_mapping.get(organization_id)
        group_names = [
            constants.Group.ORGANIZATION_GUEST,
            constants.Group.ORGANIZATION_DLP,
        ]
        if role == constants.Group.ORGANIZATION_ADMIN:
            group_names.append(constants.Group.ORGANIZATION_STAFF)

        if not user.is_superuser:
            role_filters["group__name__in"] = group_names

        queryset = queryset.filter(
            Exists(RoleAssignment.objects.filter(**role_filters))
        )
        return queryset
