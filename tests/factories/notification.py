import factory
import factory.fuzzy
from django.contrib.contenttypes.models import ContentType
from model_utils import Choices
from notifications.models import Notification

from .user import UserFactory


class NotificationFactory(factory.django.DjangoModelFactory):
    level = factory.fuzzy.FuzzyChoice(
        Choices("success", "info", "warning", "error"), getter=lambda c: c[0]
    )

    recipient = factory.SubFactory(UserFactory)

    actor = factory.SubFactory(UserFactory)

    verb = factory.Faker("text", max_nb_chars=100)

    action_object_object_id = factory.SelfAttribute("action_object.id")
    action_object_content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.action_object)
    )

    class Meta:
        exclude = ["action_object"]
        abstract = True
