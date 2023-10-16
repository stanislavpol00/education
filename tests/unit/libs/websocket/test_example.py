from notifications.models import Notification

import constants
from libs.websocket import ExampleNotificationWebsocket
from tests.base_test import BaseTestCase
from tests.factories import ExampleFactory, TipFactory


class TestExampleNotificationWebsocket(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip = TipFactory.create(added_by=cls.manager_user)

        cls.example1 = ExampleFactory.create(
            tip=cls.tip,
            added_by=cls.experimental_user,
            updated_by=cls.super_user,
        )

        cls.example2 = ExampleFactory.create(
            tip=cls.tip,
            added_by=cls.manager_user,
            updated_by=cls.manager_user,
        )

    def test_send_example_notification_to_tip_owner(self):
        # self.example1.added_by_id = self.tip.added_by_id
        old_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        ExampleNotificationWebsocket.send_example_notification_to_tip_owner(
            self.example1, updated=False
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        self.assertEqual(old_count + 1, new_count)

        # self.example1.updated_by_id = self.tip.added_by_id
        old_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        ExampleNotificationWebsocket.send_example_notification_to_tip_owner(
            self.example1, updated=True
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        self.assertEqual(old_count + 1, new_count)

    def test_send_example_notification_to_tip_owner_with_same_owner_tip(self):
        # self.example2.added_by_id = self.tip.added_by_id
        old_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        ExampleNotificationWebsocket.send_example_notification_to_tip_owner(
            self.example2, updated=False
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        self.assertEqual(old_count, new_count)

        # self.example2.updated_by_id = self.tip.added_by_id
        old_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        ExampleNotificationWebsocket.send_example_notification_to_tip_owner(
            self.example2, updated=True
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE
        ).count()
        self.assertEqual(old_count, new_count)
