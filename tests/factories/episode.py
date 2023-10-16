import factory
import pytz

from main.models import Episode

from .student import StudentFactory
from .user import UserFactory


class EpisodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Episode
        strategy = factory.CREATE_STRATEGY

    student = factory.SubFactory(StudentFactory)
    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: "title %d" % n)
    description = factory.Faker("text", max_nb_chars=24)
    date = factory.Faker("date_time", tzinfo=pytz.UTC)
