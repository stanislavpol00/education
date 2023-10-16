import factory
import pytz

from main.models import Example

from .episode import EpisodeFactory
from .tip import TipFactory
from .user import UserFactory


class ExampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Example
        strategy = factory.CREATE_STRATEGY

    tip = factory.SubFactory(TipFactory)
    description = factory.Faker("word")
    updated_by = factory.SubFactory(UserFactory)
    added_by = factory.SubFactory(UserFactory)
    episode = factory.SubFactory(EpisodeFactory)
    headline = factory.Sequence(lambda n: "headline %d" % n)
    heading = factory.Sequence(lambda n: "heading %d" % n)
    situation = factory.Sequence(lambda n: "situation %d" % n)

    created_at = factory.Faker("date_time", tzinfo=pytz.UTC)
