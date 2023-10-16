import factory

from main.models import Organization


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization
        django_get_or_create = ("name",)

    name = factory.Faker("text", max_nb_chars=30)
