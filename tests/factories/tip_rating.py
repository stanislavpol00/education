import factory

from main.models import TipRating

from .tip import TipFactory
from .user import UserFactory


class TipRatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TipRating
        strategy = factory.CREATE_STRATEGY

    tip = factory.SubFactory(TipFactory)
    added_by = factory.SubFactory(UserFactory)

    comment = factory.Faker("word")
    clarity = factory.Faker("pyint", min_value=0, max_value=5)
    relevance = factory.Faker("pyint", min_value=0, max_value=5)
    uniqueness = factory.Faker("pyint", min_value=0, max_value=5)
