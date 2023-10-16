import factory
from taggit.models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        strategy = factory.CREATE_STRATEGY

    name = factory.Faker("text", max_nb_chars=50)
    slug = factory.Faker("text", max_nb_chars=50)
