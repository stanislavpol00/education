import factory
import pytz

import constants
from main.models import StudentExample

from .episode import EpisodeFactory
from .example import ExampleFactory
from .student import StudentFactory
from .user import UserFactory


class StudentExampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentExample
        strategy = factory.CREATE_STRATEGY

    example = factory.SubFactory(ExampleFactory)
    student = factory.SubFactory(StudentFactory)
    episode = factory.SubFactory(EpisodeFactory)
    added_by = factory.SubFactory(UserFactory)

    reason = constants.StudentExample.REASON_EPISODE

    created_at = factory.Faker("date_time", tzinfo=pytz.UTC)
    updated_at = factory.Faker("date_time", tzinfo=pytz.UTC)
