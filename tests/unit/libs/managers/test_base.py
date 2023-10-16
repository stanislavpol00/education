from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from notifications.models import Notification

from main.models import Example, StudentTip, Tip
from tests.base_test import BaseTestCase
from tests.factories import (
    ExampleFactory,
    StudentTipFactory,
    TipFactory,
)


class TestBaseManager(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        content_types = ContentType.objects.get_for_models(
            Tip, Example
        )
        cls.tip_content_type = content_types[Tip].id
        cls.example_content_type = content_types[Example].id

        cls.tip1 = TipFactory.create(
            title="tip 1",
            description="description 1",
            added_by=cls.normal_user,
            updated_by=None,
        )
        cls.tip1.created_at -= timezone.timedelta(hours=24)
        cls.tip1.save()

        cls.tip1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.tip1.id,
                action_object_content_type_id=cls.tip_content_type,
                recipient=cls.normal_user,
            )
            .order_by("-timestamp")
            .first()
        )
        cls.tip1_notification.timestamp -= timezone.timedelta(hours=24)
        cls.tip1_notification.save()

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

        cls.example1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.example1.id,
                action_object_content_type_id=cls.example_content_type,
                recipient=cls.normal_user,
            )
            .order_by("-timestamp")
            .first()
        )
        cls.example1_notification.timestamp -= timezone.timedelta(hours=24)
        cls.example1_notification.save()

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

        cls.old_example_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.old_example.id,
                action_object_content_type_id=cls.example_content_type,
                recipient=cls.normal_user,
            )
            .order_by("-timestamp")
            .first()
        )
        cls.old_example_notification.timestamp -= timezone.timedelta(days=365)
        cls.old_example_notification.save()

    def test_to_dict_with_tip(self):
        tip_ids = [self.tip1.id, self.tip2.id]

        tips = Tip.objects.to_dict(ids=tip_ids)

        self.assertEqual(tips[self.tip1.id], self.tip1)
        self.assertEqual(tips[self.tip2.id], self.tip2)

    def test_to_dict_with_example(self):
        example_ids = [
            self.example1.id,
            self.example2.id,
            self.old_example.id,
        ]

        examples = Example.objects.to_dict(ids=example_ids)

        self.assertEqual(examples[self.example1.id], self.example1)
        self.assertEqual(examples[self.example2.id], self.example2)
        self.assertEqual(examples[self.old_example.id], self.old_example)

    def test_annotate_contributed_at_with_tip(self):
        activities = [{self.tip1.id: self.tip1_notification.timestamp}]

        tips = Tip.objects.annotate_contributed_at(activities=activities)

        self.assertEqual(tips[self.tip1.id], self.tip1)
        self.assertEqual(
            tips[self.tip1.id].contributed_at, self.tip1_notification.timestamp
        )

    def test_annotate_contributed_at_with_example(self):
        activities = [
            {self.example1.id: self.example1_notification.timestamp},
            {self.old_example.id: self.old_example_notification.timestamp},
        ]

        examples = Example.objects.annotate_contributed_at(
            activities=activities
        )

        self.assertEqual(examples[self.example1.id], self.example1)
        self.assertEqual(examples[self.old_example.id], self.old_example)
        self.assertEqual(
            examples[self.example1.id].contributed_at,
            self.example1_notification.timestamp,
        )
        self.assertEqual(
            examples[self.old_example.id].contributed_at,
            self.old_example_notification.timestamp,
        )

    def test_annotate_contributed_at_with_order_by(self):
        activities = [
            {self.example1.id: self.example1_notification.timestamp},
            {self.example2.id: self.example2.created_at},
            {self.old_example.id: self.old_example_notification.timestamp},
        ]

        examples = Example.objects.annotate_contributed_at(
            activities=activities
        )
        list_items = [(k, v) for k, v in examples.items()]

        self.assertEqual(list_items[0][0], self.example2.id)
        self.assertEqual(list_items[1][0], self.example1.id)
        self.assertEqual(list_items[2][0], self.old_example.id)

    def test_count_by_days_with_student_tip(self):
        student_tip1 = StudentTipFactory.create()
        student_tip1.created_at = timezone.localtime() - timezone.timedelta(
            days=1
        )
        student_tip1.save()

        student_tip2 = StudentTipFactory.create()
        student_tip2.created_at = timezone.localtime() - timezone.timedelta(
            days=30
        )
        student_tip2.save()

        # filter with default param days = 7
        result = StudentTip.objects.count_by_days()
        self.assertEqual(result[student_tip1.student_id], 1)
        self.assertNotIn(student_tip2.student_id, result)

        # filter with default param days = 365
        result = StudentTip.objects.count_by_days(days=365)
        self.assertEqual(result[student_tip1.student_id], 1)
        self.assertEqual(result[student_tip2.student_id], 1)
