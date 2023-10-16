import factory
from django.contrib.contenttypes.models import ContentType
from taggit.models import TaggedItem

from .episode import EpisodeFactory
from .example import ExampleFactory
from .student import StudentFactory
from .tag import TagFactory
from .tip import TipFactory


class TaggedItemFactory(factory.django.DjangoModelFactory):
    object_id = factory.SelfAttribute("content_object.id")
    tag = factory.SubFactory(TagFactory)
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )

    class Meta:
        exclude = ["content_object"]
        abstract = True


class TaggedTipFactory(TaggedItemFactory):
    content_object = factory.SubFactory(TipFactory)

    class Meta:
        model = TaggedItem


class TaggedExampleFactory(TaggedItemFactory):
    content_object = factory.SubFactory(ExampleFactory)

    class Meta:
        model = TaggedItem


class TaggedStudentFactory(TaggedItemFactory):
    content_object = factory.SubFactory(StudentFactory)

    class Meta:
        model = TaggedItem


class TaggedEpisodeFactory(TaggedItemFactory):
    content_object = factory.SubFactory(EpisodeFactory)

    class Meta:
        model = TaggedItem
