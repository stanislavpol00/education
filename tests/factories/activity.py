import factory
import factory.fuzzy

import constants
from main.models import Activity

from .user import UserFactory


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity
        strategy = factory.CREATE_STRATEGY

    user = factory.SubFactory(UserFactory)

    type = factory.fuzzy.FuzzyChoice(
        constants.Activity.CHOICES, getter=lambda c: c[0]
    )
