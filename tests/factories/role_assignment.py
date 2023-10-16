import factory
from django.contrib.auth.models import Group

import constants
from main.models import RoleAssignment

from .organization import OrganizationFactory
from .user import UserFactory


class RoleAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoleAssignment
        strategy = factory.CREATE_STRATEGY
        django_get_or_create = ("user", "organization")

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)

    @classmethod
    def _generate(cls, strategy, kwargs):
        if "group" not in kwargs:
            kwargs["group"] = Group.objects.get(
                name=constants.Group.ORGANIZATION_GUEST
            )
        return super()._generate(strategy, kwargs)
