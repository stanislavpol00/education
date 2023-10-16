import factory

from main.models import UserStudentMapping

from .student import StudentFactory
from .user import UserFactory


class UserStudentMappingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserStudentMapping
        strategy = factory.CREATE_STRATEGY

    student = factory.SubFactory(StudentFactory)
    user = factory.SubFactory(UserFactory)
