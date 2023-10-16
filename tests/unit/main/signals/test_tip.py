from notifications.models import Notification

import constants
from tests.base_test import BaseTestCase
from tests.factories import TipFactory


class TestTip(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.tip = TipFactory.create(
            title="tip by experimental teacher",
            added_by=cls.experimental_user,
        )
        cls.tip1 = TipFactory.create()

    def test_post_save_by_teacher_check_send_notification(self):
        expected_experimental_received = {
            "sender_id": self.tip.added_by.id,
            "recipient_id": self.tip.added_by.id,
            "description": "You have created a new tip {}".format(
                self.tip.title,
            ),
            "verb": constants.Activity.CREATE_TIP,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_experimental_received["sender_id"],
            recipient_id=expected_experimental_received["recipient_id"],
            description=expected_experimental_received["description"],
            verb=expected_experimental_received["verb"],
        )
        self.assertTrue(is_existed)

        expected_manager_user_received = {
            "sender_id": self.tip.added_by.id,
            "recipient_id": self.manager_user.id,
            "description": "Teacher {} has created a new tip {}".format(
                self.tip.added_by.full_name,
                self.tip.title,
            ),
            "verb": constants.Activity.CREATE_TIP,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_manager_user_received["sender_id"],
            recipient_id=expected_manager_user_received["recipient_id"],
            description=expected_manager_user_received["description"],
            verb=expected_manager_user_received["verb"],
        )
        self.assertTrue(is_existed)

    def test_post_save_signal_with_send_notification_fail_none_added_by(
        self,
    ):
        tip = TipFactory.create(added_by=None)
        expected = {
            "sender_id": self.experimental_user.id,
            "description": "You have created a new tip {}".format(
                tip.title,
            ),
            "verb": constants.Activity.CREATE_TIP,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=str(expected["sender_id"]),
            description=expected["description"],
            verb=expected["verb"],
        )
        self.assertFalse(is_existed)

    def test_post_update_by_owner_check_send_notification(self):
        self.tip.description = "description update"
        self.tip.updated_by = self.experimental_user
        self.tip.save()

        expected = {
            "sender_id": self.tip.updated_by.id,
            "recipient_id": self.tip.added_by.id,
            "description": "You just have updated tip {}".format(
                self.tip.title
            ),
            "verb": constants.Activity.UPDATE_TIP,
        }

        is_existed = Notification.objects.filter(
            actor_object_id=expected["sender_id"],
            recipient_id=expected["recipient_id"],
            description=expected["description"],
            verb=expected["verb"],
        )
        self.assertTrue(is_existed)

    def test_post_update_by_other_teacher_check_send_notification(self):
        self.tip.description = "description update"
        self.tip.updated_by = self.other_experimental_user
        self.tip.save()

        expected = {
            "sender_id": self.tip.updated_by.id,
            "recipient_id": self.tip.added_by.id,
            "description": "Your tip {} is updated by Teacher {}".format(
                self.tip.title,
                self.other_experimental_user.full_name,
            ),
            "verb": constants.Activity.UPDATE_TIP,
        }

        is_existed = Notification.objects.filter(
            actor_object_id=expected["sender_id"],
            recipient_id=expected["recipient_id"],
            description=expected["description"],
            verb=expected["verb"],
        )
        self.assertTrue(is_existed)

    # check send notification fail with none added_by and updated_by
    def test_post_update_signal_with_send_notification_fail_none_modifier(
        self,
    ):
        self.tip1.title = "title update"
        self.tip1.save()
        self.tip1.refresh_from_db()

        expected = {
            "sender_id": self.tip1.updated_by.id,
            "descriptions": [
                "You just have updated example {}".format(self.tip1.title),
                "Your example {} is updated by Teacher {}".format(
                    self.tip1.title,
                    self.other_experimental_user.full_name,
                ),
            ],
            "verb": constants.Activity.UPDATE_TIP,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=str(expected["sender_id"]),
            description__in=[expected["descriptions"]],
            verb=expected["verb"],
        )
        self.assertFalse(is_existed)

    def test_pre_save_with_update_marked_for_editing_check_websocket_notification(
        self,
    ):
        old_count = Notification.objects.filter(
            actor_object_id=self.tip.updated_by.id,
            recipient=self.tip.added_by,
            verb=constants.Activity.SET_TIP_EDIT_MARK,
            description="Tip {} was marked for editing".format(self.tip.title),
        ).count()

        self.tip.marked_for_editing = True
        self.tip.updated_by = self.manager_user
        self.tip.save()

        new_count = Notification.objects.filter(
            actor_object_id=self.tip.updated_by.id,
            recipient=self.tip.added_by,
            verb=constants.Activity.SET_TIP_EDIT_MARK,
            description="Tip {} was marked for editing".format(self.tip.title),
        ).count()
        self.assertEqual(old_count + 1, new_count)

    def test_pre_save_with_update_marked_for_editing_check_user_action(self):
        old_count = Notification.objects.filter(
            actor_object_id=self.tip.updated_by.id,
            recipient=self.tip.updated_by,
            verb=constants.Activity.SET_TIP_EDIT_MARK,
            description="You were marked tip {} for editing".format(
                self.tip.title
            ),
        ).count()

        self.tip.marked_for_editing = True
        self.tip.updated_by = self.manager_user
        self.tip.save()

        new_count = Notification.objects.filter(
            actor_object_id=self.tip.updated_by.id,
            recipient=self.tip.updated_by,
            verb=constants.Activity.SET_TIP_EDIT_MARK,
            description="You were marked tip {} for editing".format(
                self.tip.title
            ),
        ).count()
        self.assertEqual(old_count + 1, new_count)

    def test_pre_save_with_update_marked_for_editing_check_dont_send_websocket_notification(
        self,
    ):
        old_count = Notification.objects.filter(
            actor_object_id=self.tip.updated_by.id,
            recipient=self.tip.updated_by,
            verb=constants.Activity.SET_TIP_EDIT_MARK,
            description="Tip {} was marked for editing".format(self.tip.title),
        ).count()

        self.tip.marked_for_editing = True
        self.tip.updated_by = self.experimental_user
        self.tip.save()

        new_count = Notification.objects.filter(
            actor_object_id=self.tip.updated_by.id,
            recipient=self.tip.updated_by,
            verb=constants.Activity.SET_TIP_EDIT_MARK,
            description="Tip {} was marked for editing".format(self.tip.title),
        ).count()
        self.assertEqual(old_count, new_count)

    def test_pre_save_with_check_attach_tip_notifications(self):
        tip1 = TipFactory.create()
        tip2 = TipFactory.create()
        tip = TipFactory.create(updated_by=self.manager_user)
        tip.linked_tips.add(tip1, tip2)

        old_count = Notification.objects.filter(
            actor_object_id=tip.updated_by.id,
            recipient=tip.updated_by,
            verb=constants.Activity.ATTACH_RELATED_TIPS_WITH_TIP,
        ).count()

        tip3 = TipFactory.create()
        tip.linked_tips.add(tip3)

        new_count = Notification.objects.filter(
            actor_object_id=tip.updated_by.id,
            recipient=tip.updated_by,
            verb=constants.Activity.ATTACH_RELATED_TIPS_WITH_TIP,
        ).count()

        self.assertEqual(old_count + 1, new_count)

    def test_pre_save_with_check_detach_tip_notifications(self):
        tip = TipFactory.create(updated_by=self.manager_user)
        tip1 = TipFactory.create()
        tip2 = TipFactory.create()
        tip.linked_tips.add(tip1, tip2)

        old_count = Notification.objects.filter(
            actor_object_id=tip.updated_by.id,
            recipient=tip.updated_by,
            verb=constants.Activity.DETACH_RELATED_TIPS_WITH_TIP,
        ).count()

        tip.linked_tips.remove(tip2)

        new_count = Notification.objects.filter(
            actor_object_id=tip.updated_by.id,
            recipient=tip.updated_by,
            verb=constants.Activity.DETACH_RELATED_TIPS_WITH_TIP,
        ).count()

        self.assertEqual(old_count + 1, new_count)
