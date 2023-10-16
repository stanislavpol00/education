import factory
import pytz

from main.models import StudentTip

from .student import StudentFactory
from .tip import TipFactory
from .user import UserFactory


class StudentTipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentTip
        strategy = factory.CREATE_STRATEGY

    tip = factory.SubFactory(TipFactory)
    student = factory.SubFactory(StudentFactory)
    added_by = factory.SubFactory(UserFactory)

    created_at = factory.Faker("date_time", tzinfo=pytz.UTC)
    updated_at = factory.Faker("date_time", tzinfo=pytz.UTC)
