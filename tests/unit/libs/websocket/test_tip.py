from notifications.models import Notification

import constants
from libs.websocket import TipNotificationWebsocket
from tests.base_test import BaseTestCase
from tests.factories import TipFactory


class TestTipNotificationWebsocket(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip1 = TipFactory.create(
            added_by=cls.manager_user,
            updated_by=cls.super_user,
        )
        cls.tip2 = TipFactory.create(
            added_by=cls.manager_user,
            updated_by=cls.manager_user,
        )

    def test_send_editing_notification_to_tip_owner(self):
        old_count = Notification.objects.filter(
            verb=constants.Activity.SET_TIP_EDIT_MARK
        ).count()

        TipNotificationWebsocket.send_editing_notification_to_tip_owner(
            self.tip1
        )

        count = Notification.objects.filter(
            verb=constants.Activity.SET_TIP_EDIT_MARK
        ).count()
        self.assertEqual(old_count + 1, count)

    def test_send_editing_notification_to_tip_owner_with_updated_user_is_owner_tip(
        self,
    ):
        old_count = Notification.objects.filter(
            verb=constants.Activity.SET_TIP_EDIT_MARK
        ).count()

        TipNotificationWebsocket.send_editing_notification_to_tip_owner(
            self.tip2
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.SET_TIP_EDIT_MARK
        ).count()
        self.assertEqual(old_count, new_count)
