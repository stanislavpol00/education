from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from notifications.models import Notification
from rest_framework import status

from main.models import Example, Tip
from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory, TipFactory


class TestRecentActivityAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url = reverse("v1:recent-activities")

        content_types = ContentType.objects.get_for_models(
            Tip, Example
        )
        tip_content_type = content_types[Tip].id
        example_content_type = content_types[Example].id

        cls.tip1 = TipFactory.create(
            title="tip 1",
            description="description 1",
            added_by=cls.normal_user,
            updated_by=None,
        )
        cls.tip1.created_at -= timezone.timedelta(hours=24)
        cls.tip1.save()

        tip1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.tip1.id,
                action_object_content_type_id=tip_content_type,
                recipient=cls.normal_user,
            )
            .order_by("-timestamp")
            .first()
        )
        tip1_notification.timestamp -= timezone.timedelta(hours=24)
        tip1_notification.save()

        cls.tip2 = TipFactory.create(
            title="tip 2",
            description="description 2",
            added_by=cls.normal_user,
            updated_by=None,
        )

        cls.example1 = ExampleFactory.create(
            description="example 1",
            added_by=cls.normal_user,
            tip=None,
            episode=None,
            updated_by=None,
        )
        cls.example1.created_at -= timezone.timedelta(hours=24)
        cls.example1.save()

        example1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.example1.id,
                action_object_content_type_id=example_content_type,
                recipient=cls.normal_user,
            )
            .order_by("-timestamp")
            .first()
        )
        example1_notification.timestamp -= timezone.timedelta(hours=24)
        example1_notification.save()

        cls.example2 = ExampleFactory.create(
            description="example 2",
            added_by=cls.normal_user,
            tip=None,
            episode=None,
            updated_by=None,
        )

        cls.old_example = ExampleFactory.create(
            added_by=cls.normal_user, tip=None, episode=None, updated_by=None
        )
        cls.old_example.created_at -= timezone.timedelta(days=365)
        cls.old_example.save()

        old_example_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.old_example.id,
                action_object_content_type_id=example_content_type,
                recipient=cls.normal_user,
            )
            .order_by("-timestamp")
            .first()
        )
        old_example_notification.timestamp -= timezone.timedelta(days=365)
        old_example_notification.save()

        cls.keys = [
            "tips",
            "examples",
        ]

        cls.tip_keys = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "contributed_at",
        ]

        cls.example_keys = [
            "id",
            "tip",
            "description",
            "example_type",
            "context_notes",
            "sounds_like",
            "looks_like",
            "episode",
            "is_active",
            "goal",
            "is_workflow_completed",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
            "updated_by",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
            "contributed_at",
        ]

    def test_get_success_check_keys(self):
        response = self.forced_authenticated_client.get(
            self.url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        keys = list(data.keys())
        self.assertEqual(sorted(keys), sorted(self.keys))

        tip_keys = list(set().union(*(tip.keys() for tip in data["tips"])))
        self.assertEqual(sorted(tip_keys), sorted(self.tip_keys))

        example_keys = list(
            set().union(*(example.keys() for example in data["examples"]))
        )
        self.assertEqual(sorted(example_keys), sorted(self.example_keys))

    def test_get_success(self):
        response = self.forced_authenticated_client.get(
            self.url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        tips_id = [tip["id"] for tip in data["tips"]]
        examples_id = [example["id"] for example in data["examples"]]

        self.assertIn(self.tip1.id, tips_id)
        self.assertIn(self.tip2.id, tips_id)

        self.assertIn(self.example1.id, examples_id)
        self.assertIn(self.example2.id, examples_id)
        self.assertIn(self.old_example.id, examples_id)

    def test_get_success_with_filter_start_date(self):
        date_params = {
            "start_date": timezone.now() - timezone.timedelta(days=5)
        }
        response = self.forced_authenticated_client.get(
            self.url, data=date_params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        tips_id = [tip["id"] for tip in data["tips"]]
        examples_id = [example["id"] for example in data["examples"]]

        self.assertIn(self.tip1.id, tips_id)
        self.assertIn(self.tip2.id, tips_id)

        self.assertIn(self.example1.id, examples_id)
        self.assertIn(self.example2.id, examples_id)
        self.assertNotIn(self.old_example.id, examples_id)

    def test_get_success_with_filter_end_date(self):
        date_params = {"end_date": timezone.now() - timezone.timedelta(days=5)}
        response = self.forced_authenticated_client.get(
            self.url, data=date_params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        tips_id = [tip["id"] for tip in data["tips"]]
        examples_id = [example["id"] for example in data["examples"]]

        self.assertNotIn(self.tip1.id, tips_id)
        self.assertNotIn(self.tip2.id, tips_id)

        self.assertNotIn(self.example1.id, examples_id)
        self.assertNotIn(self.example2.id, examples_id)
        self.assertIn(self.old_example.id, examples_id)

    def test_get_success_with_filter_date(self):
        date_params = {
            "start_date": timezone.now() - timezone.timedelta(days=364),
            "end_date": timezone.now() - timezone.timedelta(hours=1),
        }
        response = self.forced_authenticated_client.get(
            self.url, data=date_params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        tips_id = [tip["id"] for tip in data["tips"]]
        examples_id = [example["id"] for example in data["examples"]]

        self.assertIn(self.tip1.id, tips_id)
        self.assertNotIn(self.tip2.id, tips_id)

        self.assertIn(self.example1.id, examples_id)
        self.assertNotIn(self.example2.id, examples_id)
        self.assertNotIn(self.old_example.id, examples_id)

    def test_get_success_with_order_by_contributed_at(self):
        response = self.forced_authenticated_client.get(
            self.url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.data
        tips_id = [tip["id"] for tip in data["tips"]]
        examples_id = [example["id"] for example in data["examples"]]

        self.assertEqual(self.tip2.id, tips_id[0])
        self.assertEqual(self.tip1.id, tips_id[1])

        self.assertEqual(self.example2.id, examples_id[0])
        self.assertEqual(self.example1.id, examples_id[1])
        self.assertEqual(self.old_example.id, examples_id[2])
