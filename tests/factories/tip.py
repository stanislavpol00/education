import factory

from main.models import Tip

from .user import UserFactory


class TipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tip
        strategy = factory.CREATE_STRATEGY

    title = factory.Sequence(lambda n: "title %d" % n)
    description = factory.Sequence(lambda n: "description %d" % n)
    updated_by = factory.SubFactory(UserFactory)
    added_by = factory.SubFactory(UserFactory)
