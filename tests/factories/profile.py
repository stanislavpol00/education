import factory
import factory.fuzzy

import constants
from main.models import Profile

from .user import UserFactory


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        strategy = factory.CREATE_STRATEGY

    user = factory.SubFactory(UserFactory)
    usertype = factory.fuzzy.FuzzyChoice(
        constants.UserType.CHOICES, getter=lambda c: c[0]
    )
    photo_width = factory.Faker("random_number", digits=2)
    photo_height = factory.Faker("random_number", digits=2)
    photo = factory.django.ImageField(width=photo_width, height=photo_height)
