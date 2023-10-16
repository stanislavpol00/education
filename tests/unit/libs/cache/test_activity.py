from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from notifications.models import Notification

from main.models import Example, Tip
from libs.cache import ActivityCache
from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory, TipFactory


class TestActivity(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        content_types = ContentType.objects.get_for_models(
            Tip, Example
        )
        cls.tip_content_type = content_types[Tip].id
        cls.example_content_type = content_types[Example].id

        cls.user_ids = [cls.normal_user.id, cls.manager_user.id]

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
                level="success",
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
                level="success",
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
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        cls.old_example_notification.timestamp -= timezone.timedelta(days=365)
        cls.old_example_notification.save()

        # of admin and manager
        cls.tip3 = TipFactory.create(
            title="tip 3 of admin and manager",
            description="description 3 of admin and manager",
            added_by=cls.manager_user,
            updated_by=None,
        )
        cls.tip3.created_at -= timezone.timedelta(hours=24)
        cls.tip3.save()
        cls.tip3_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.tip3.id,
                action_object_content_type_id=cls.tip_content_type,
                recipient=cls.manager_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        cls.tip3_notification.timestamp -= timezone.timedelta(hours=24)
        cls.tip3_notification.save()

        cls.tip4 = TipFactory.create(
            title="tip 4 of admin and manager",
            description="description 4 of admin and manager",
            added_by=cls.manager_user,
            updated_by=None,
        )

        cls.example3 = ExampleFactory.create(
            description="example 3 of admin and manager",
            added_by=cls.manager_user,
            tip=None,
            episode=None,
            updated_by=None,
        )
        cls.example3.created_at -= timezone.timedelta(hours=24)
        cls.example3.save()

        cls.example3_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.example3.id,
                action_object_content_type_id=cls.example_content_type,
                recipient=cls.manager_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        cls.example3_notification.timestamp -= timezone.timedelta(hours=24)
        cls.example3_notification.save()

        cls.example4 = ExampleFactory.create(
            description="example 4 of admin and manager",
            added_by=cls.manager_user,
            tip=None,
            episode=None,
            updated_by=None,
        )

        cls.old_example1 = ExampleFactory.create(
            added_by=cls.manager_user, tip=None, episode=None, updated_by=None
        )
        cls.old_example1.created_at -= timezone.timedelta(days=365)
        cls.old_example1.save()

        cls.old_example1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.old_example1.id,
                action_object_content_type_id=cls.example_content_type,
                recipient=cls.manager_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        cls.old_example1_notification.timestamp -= timezone.timedelta(days=365)
        cls.old_example1_notification.save()

    def get_ids_by_user(self, activities, content_type):
        if content_type not in activities:
            return []

        activities = activities[content_type]
        ids = set().union(*(activity.keys() for activity in activities))

        return ids

    def get_ids_user_activities(self, activities, user_id, content_type):
        if user_id not in activities:
            return []
        if content_type not in activities[user_id]:
            return []

        ids = set().union(
            *(
                activity.keys()
                for activity in activities[user_id][content_type]
            )
        )

        return ids

    def test_get_activities_by_user_with_normal_user(self):
        activities = ActivityCache.get_activities_by_user(self.normal_user.id)

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

        self.assertIn(self.example1.id, example_ids)
        self.assertIn(self.example2.id, example_ids)
        self.assertIn(self.old_example.id, example_ids)

        # check with manager
        self.assertNotIn(self.tip3.id, tip_ids)
        self.assertNotIn(self.tip4.id, tip_ids)

        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertNotIn(self.old_example1.id, example_ids)

    def test_get_activities_by_user_with_normal_user_and_filter_start_date(
        self,
    ):
        activities = ActivityCache.get_activities_by_user(
            user_id=self.normal_user.id,
            start_date=timezone.now() - timezone.timedelta(days=5),
        )

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

        self.assertIn(self.example1.id, example_ids)
        self.assertIn(self.example2.id, example_ids)
        self.assertNotIn(self.old_example.id, example_ids)


        # check with manager
        self.assertNotIn(self.tip3.id, tip_ids)
        self.assertNotIn(self.tip4.id, tip_ids)

        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertNotIn(self.old_example1.id, example_ids)


    def test_get_activities_by_user_with_normal_user_and_filter_end_date(self):
        activities = ActivityCache.get_activities_by_user(
            user_id=self.normal_user.id,
            end_date=timezone.now() - timezone.timedelta(days=5),
        )

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertIn(self.old_example.id, example_ids)


        # check with manager
        self.assertNotIn(self.tip3.id, tip_ids)
        self.assertNotIn(self.tip4.id, tip_ids)

        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertNotIn(self.old_example1.id, example_ids)


    def test_get_activities_by_user_with_normal_user_and_filter_date(self):
        activities = ActivityCache.get_activities_by_user(
            user_id=self.normal_user.id,
            start_date=timezone.now() - timezone.timedelta(days=364),
            end_date=timezone.now() - timezone.timedelta(days=1),
        )

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        self.assertIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.old_example.id, example_ids)


        # check with manager
        self.assertNotIn(self.tip3.id, tip_ids)
        self.assertNotIn(self.tip4.id, tip_ids)

        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertNotIn(self.old_example1.id, example_ids)


    def test_get_activities_by_user_with_manager_user(self):
        activities = ActivityCache.get_activities_by_user(self.manager_user.id)

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.old_example.id, example_ids)

        # check with manager
        self.assertIn(self.tip3.id, tip_ids)
        self.assertIn(self.tip4.id, tip_ids)

        self.assertIn(self.example3.id, example_ids)
        self.assertIn(self.example4.id, example_ids)
        self.assertIn(self.old_example1.id, example_ids)


    def test_get_activities_by_user_with_manager_user_and_filter_start_date(
        self,
    ):
        activities = ActivityCache.get_activities_by_user(
            user_id=self.manager_user.id,
            start_date=timezone.now() - timezone.timedelta(days=5),
        )

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.old_example.id, example_ids)

        # check with manager
        self.assertIn(self.tip3.id, tip_ids)
        self.assertIn(self.tip4.id, tip_ids)

        self.assertIn(self.example3.id, example_ids)
        self.assertIn(self.example4.id, example_ids)
        self.assertNotIn(self.old_example1.id, example_ids)


    def test_get_activities_by_user_with_manager_user_and_filter_end_date(
        self,
    ):
        activities = ActivityCache.get_activities_by_user(
            user_id=self.manager_user.id,
            end_date=timezone.now() - timezone.timedelta(days=5),
        )

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.old_example.id, example_ids)


        # check with manager
        self.assertNotIn(self.tip3.id, tip_ids)
        self.assertNotIn(self.tip4.id, tip_ids)

        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertIn(self.old_example1.id, example_ids)


    def test_get_activities_by_user_with_manager_user_and_filter_date(self):
        activities = ActivityCache.get_activities_by_user(
            user_id=self.manager_user.id,
            start_date=timezone.now() - timezone.timedelta(days=364),
            end_date=timezone.now() - timezone.timedelta(days=1),
        )

        tip_ids = self.get_ids_by_user(activities, self.tip_content_type)
        example_ids = self.get_ids_by_user(
            activities, self.example_content_type
        )

        # check with normal user
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.old_example.id, example_ids)


        # check with manager
        self.assertIn(self.tip3.id, tip_ids)
        self.assertNotIn(self.tip4.id, tip_ids)

        self.assertIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertNotIn(self.old_example1.id, example_ids)


    def test_get_user_activities_check_mount_timestamp(self):
        activities = ActivityCache.get_user_activities(user_ids=self.user_ids)

        normal_user_activity = activities[self.normal_user.id]
        tip_activities = normal_user_activity[self.tip_content_type]
        example_activities = normal_user_activity[self.example_content_type]

        tip_activities_timestamp = list(
            set().union(
                *(tip_activity.values() for tip_activity in tip_activities)
            )
        )

        example_activities_timestamp = list(
            set().union(
                *(
                    example_activity.values()
                    for example_activity in example_activities
                )
            )
        )

        self.assertIn(
            self.tip1_notification.timestamp, tip_activities_timestamp
        )

        self.assertIn(
            self.example1_notification.timestamp, example_activities_timestamp
        )
        self.assertIn(
            self.old_example_notification.timestamp,
            example_activities_timestamp,
        )

    def test_get_user_activities(self):
        activities = ActivityCache.get_user_activities(user_ids=self.user_ids)

        tip_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.tip_content_type
        )
        example_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.example_content_type
        )

        # check with normal user
        self.assertIn(self.tip1.id, tip_ids_by_normal_user)
        self.assertIn(self.tip2.id, tip_ids_by_normal_user)

        self.assertIn(self.example1.id, example_ids_by_normal_user)
        self.assertIn(self.example2.id, example_ids_by_normal_user)
        self.assertIn(self.old_example.id, example_ids_by_normal_user)


        tip_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.tip_content_type
        )
        example_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.example_content_type
        )

        # check with manager
        self.assertIn(self.tip3.id, tip_ids_by_manager_user)
        self.assertIn(self.tip4.id, tip_ids_by_manager_user)

        self.assertIn(self.example3.id, example_ids_by_manager_user)
        self.assertIn(self.example4.id, example_ids_by_manager_user)
        self.assertIn(self.old_example1.id, example_ids_by_manager_user)


    def test_get_user_activities_check_filter_user_ids(self):
        activities = ActivityCache.get_user_activities(user_ids=[])

        tip_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.tip_content_type
        )
        example_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.example_content_type
        )

        # check with normal user
        self.assertEqual([], tip_ids_by_normal_user)
        self.assertEqual([], example_ids_by_normal_user)

        tip_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.tip_content_type
        )
        example_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.example_content_type
        )
        # check with manager
        self.assertEqual([], tip_ids_by_manager_user)
        self.assertEqual([], example_ids_by_manager_user)

    def test_get_user_activities_with_filter_start_date(self):
        activities = ActivityCache.get_user_activities(
            user_ids=self.user_ids,
            start_date=timezone.now() - timezone.timedelta(days=5),
        )

        tip_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.tip_content_type
        )
        example_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.example_content_type
        )

        # check with normal user
        self.assertIn(self.tip1.id, tip_ids_by_normal_user)
        self.assertIn(self.tip2.id, tip_ids_by_normal_user)

        self.assertIn(self.example1.id, example_ids_by_normal_user)
        self.assertIn(self.example2.id, example_ids_by_normal_user)
        self.assertNotIn(self.old_example.id, example_ids_by_normal_user)


        tip_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.tip_content_type
        )
        example_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.example_content_type
        )

        # check with manager
        self.assertIn(self.tip3.id, tip_ids_by_manager_user)
        self.assertIn(self.tip4.id, tip_ids_by_manager_user)

        self.assertIn(self.example3.id, example_ids_by_manager_user)
        self.assertIn(self.example4.id, example_ids_by_manager_user)
        self.assertNotIn(self.old_example1.id, example_ids_by_manager_user)


    def test_get_user_activities_with_filter_end_date(self):
        activities = ActivityCache.get_user_activities(
            user_ids=self.user_ids,
            end_date=timezone.now() - timezone.timedelta(days=5),
        )

        tip_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.tip_content_type
        )
        example_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.example_content_type
        )

        # check with normal user
        self.assertNotIn(self.tip1.id, tip_ids_by_normal_user)
        self.assertNotIn(self.tip2.id, tip_ids_by_normal_user)

        self.assertNotIn(self.example1.id, example_ids_by_normal_user)
        self.assertNotIn(self.example2.id, example_ids_by_normal_user)
        self.assertIn(self.old_example.id, example_ids_by_normal_user)


        tip_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.tip_content_type
        )
        example_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.example_content_type
        )

        # check with manager
        self.assertNotIn(self.tip3.id, tip_ids_by_manager_user)
        self.assertNotIn(self.tip4.id, tip_ids_by_manager_user)

        self.assertNotIn(self.example3.id, example_ids_by_manager_user)
        self.assertNotIn(self.example4.id, example_ids_by_manager_user)
        self.assertIn(self.old_example1.id, example_ids_by_manager_user)


    def test_get_user_activities_with_filter_date(self):
        activities = ActivityCache.get_user_activities(
            user_ids=self.user_ids,
            start_date=timezone.now() - timezone.timedelta(days=364),
            end_date=timezone.now() - timezone.timedelta(days=1),
        )

        tip_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.tip_content_type
        )
        example_ids_by_normal_user = self.get_ids_user_activities(
            activities, self.normal_user.id, self.example_content_type
        )

        # check with normal user
        self.assertIn(self.tip1.id, tip_ids_by_normal_user)
        self.assertNotIn(self.tip2.id, tip_ids_by_normal_user)

        self.assertIn(self.example1.id, example_ids_by_normal_user)
        self.assertNotIn(self.example2.id, example_ids_by_normal_user)
        self.assertNotIn(self.old_example.id, example_ids_by_normal_user)


        tip_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.tip_content_type
        )
        example_ids_by_manager_user = self.get_ids_user_activities(
            activities, self.manager_user.id, self.example_content_type
        )

        # check with manager
        self.assertIn(self.tip3.id, tip_ids_by_manager_user)
        self.assertNotIn(self.tip4.id, tip_ids_by_manager_user)

        self.assertIn(self.example3.id, example_ids_by_manager_user)
        self.assertNotIn(self.example4.id, example_ids_by_manager_user)
        self.assertNotIn(self.old_example1.id, example_ids_by_manager_user)

