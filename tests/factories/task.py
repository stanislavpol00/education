import factory
import pytz

import constants
from main.models import Task

from .student import StudentFactory
from .tip import TipFactory
from .user import UserFactory


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task
        strategy = factory.CREATE_STRATEGY

    tip = factory.SubFactory(TipFactory)
    student = factory.SubFactory(StudentFactory)
    added_by = factory.SubFactory(UserFactory)
    user = factory.SubFactory(UserFactory)

    created_at = factory.Faker("date_time", tzinfo=pytz.UTC)

    info = factory.Sequence(lambda n: "info %d" % n)
    task_type = constants.TaskType.EXAMPLE
