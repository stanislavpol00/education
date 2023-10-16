import factory
from django.conf import settings


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        strategy = factory.CREATE_STRATEGY

    email = factory.Sequence(lambda n: "email_%d@gmail.com" % n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: "username_%d" % n)
