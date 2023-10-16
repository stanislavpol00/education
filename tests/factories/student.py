import factory

from main.models import Student

from .user import UserFactory


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student
        strategy = factory.CREATE_STRATEGY

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    nickname = factory.Faker("user_name")

    added_by = factory.SubFactory(UserFactory)
