from django.urls import reverse
from reversion.models import Version

from tasks import version
from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory, TipFactory


class TestVersionTasks(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip = TipFactory.create(title="title")
        cls.example = ExampleFactory.create(description="description")

        cls.tip_detail_url = reverse("v1:tips-detail", args=[cls.tip.id])
        cls.example_detail_url = reverse(
            "v1:examples-detail", args=[cls.example.id]
        )

    def test_delete_versions(self):
        # create 12 versions for tip
        for i in range(12):
            data = {"title": "new title {}".format(i)}
            self.forced_authenticated_client.patch(
                self.tip_detail_url, data=data, format="json"
            )
        # create 12 versions for example
        for i in range(12):
            data = {"description": "new description {}".format(i)}
            self.forced_authenticated_client.patch(
                self.example_detail_url, data=data, format="json"
            )

        version.delete_versions()
        tip_version_count = Version.objects.get_for_object(self.tip).count()
        example_version_count = Version.objects.get_for_object(
            self.example
        ).count()

        self.assertEqual(10, tip_version_count)
        self.assertEqual(10, example_version_count)
