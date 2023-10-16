import factory

from main.models import ExampleRating

from .example import ExampleFactory
from .user import UserFactory


class ExampleRatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExampleRating
        strategy = factory.CREATE_STRATEGY

    example = factory.SubFactory(ExampleFactory)
    added_by = factory.SubFactory(UserFactory)

    comment = factory.Faker("word")
    clarity = factory.Faker("pyint", min_value=0, max_value=5)
    recommended = factory.Faker("pyint", min_value=0, max_value=5)
