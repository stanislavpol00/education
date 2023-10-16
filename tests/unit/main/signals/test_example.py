from django.utils.translation import gettext as _
from notifications.models import Notification

import constants
from main.models import StudentExample, StudentTip
from tests.base_test import BaseTestCase
from tests.factories import (
    EpisodeFactory,
    ExampleFactory,
    StudentTipFactory,
    TipFactory,
)


class TestExample(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.example = ExampleFactory.create(
            added_by=cls.experimental_user, updated_by=None
        )

        cls.example1 = ExampleFactory.create(
            added_by=cls.normal_user, updated_by=None
        )

    def test_post_save_signal_with_new_student_tip(self):
        old_student_tips_count = StudentTip.objects.count()

        example = ExampleFactory.create()

        new_student_tips_count = StudentTip.objects.count()
        self.assertEqual(old_student_tips_count + 1, new_student_tips_count)

        existed = StudentTip.objects.filter(
            tip_id=example.tip_id, student_id=example.episode.student_id
        ).exists()
        self.assertTrue(existed)

    def test_post_save_signal_with_existing_student_tip(self):
        student_tip = StudentTipFactory.create()
        episode = EpisodeFactory.create(student=student_tip.student)

        old_student_tips_count = StudentTip.objects.count()

        ExampleFactory.create(tip=student_tip.tip, episode=episode)

        new_student_tips_count = StudentTip.objects.count()
        self.assertEqual(old_student_tips_count, new_student_tips_count)

    def test_post_save_signal_with_existing_student_example(self):
        old_student_tips_count = StudentTip.objects.count()

        tip = TipFactory.create()
        episode = EpisodeFactory.create()
        student = episode.student
        example = ExampleFactory.create(tip=None, episode=episode)

        new_student_tips_count = StudentTip.objects.count()
        self.assertEqual(old_student_tips_count, new_student_tips_count)

        student_example_is_existed = StudentExample.objects.filter(
            example=example, student=student
        ).exists()
        self.assertTrue(student_example_is_existed)

        student_tip_is_existed = StudentTip.objects.filter(
            tip=tip, student=student
        ).exists()
        self.assertFalse(student_tip_is_existed)

        example.tip_id = tip.id
        example.save()

        new_student_tips_count = StudentTip.objects.count()
        self.assertEqual(old_student_tips_count + 1, new_student_tips_count)

        student_tip_is_existed = StudentTip.objects.filter(
            tip=tip, student=student
        ).exists()
        self.assertTrue(student_tip_is_existed)

    def test_post_save_signal_with_send_notification_success(self):
        expected_experimental_received = {
            "sender_id": str(self.example.added_by.id),
            "recipient_id": self.example.added_by.id,
            "description": _(
                "You have created a new example {headline}"
            ).format(headline=self.example.headline),
            "verb": constants.Activity.CREATE_EXAMPLE,
            "action_object_object_id": self.example.id,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_experimental_received["sender_id"],
            recipient_id=expected_experimental_received["recipient_id"],
            description=expected_experimental_received["description"],
            action_object_object_id=expected_experimental_received[
                "action_object_object_id"
            ],
            verb=constants.Activity.CREATE_EXAMPLE,
        ).exists()
        self.assertTrue(is_existed)

        expected_manager_user_received = {
            "sender_id": str(self.example.added_by.id),
            "recipient_id": self.manager_user.id,
            "description": _(
                "Teacher {user_fullname} has created "
                "a new example {headline}"
            ).format(
                user_fullname=self.example.added_by.full_name,
                headline=self.example.headline,
            ),
            "verb": constants.Activity.CREATE_EXAMPLE,
            "action_object_object_id": self.example.id,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_manager_user_received["sender_id"],
            recipient_id=expected_manager_user_received["recipient_id"],
            description=expected_manager_user_received["description"],
            action_object_object_id=expected_manager_user_received[
                "action_object_object_id"
            ],
            verb=constants.Activity.CREATE_EXAMPLE,
        ).exists()

        self.assertTrue(is_existed)

    def test_post_save_signal_with_send_notification_fail_none_added_by(self):
        expected = {
            "sender_id": self.example1.added_by.id,
            "description": _(
                "You have created a new example {headline}"
            ).format(headline=self.example1.headline),
            "verb": constants.Activity.CREATE_EXAMPLE,
            "action_object_object_id": self.example1.id,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=str(expected["sender_id"]),
            verb=expected["verb"],
            action_object_object_id=self.example1,
            description=expected["description"],
        ).exists()
        self.assertFalse(is_existed)

    def test_post_update_by_owner_with_send_notification(self):
        self.example.updated_by = self.experimental_user
        self.example.save()
        self.example.refresh_from_db()

        expected = {
            "sender_id": self.example.added_by.id,
            "recipient_id": self.example.added_by.id,
            "description": _(
                "You just have updated example {headline}"
            ).format(headline=self.example.headline),
            "verb": constants.Activity.UPDATE_EXAMPLE,
            "action_object_object_id": self.example.id,
        }

        is_existed = Notification.objects.filter(
            actor_object_id=expected["sender_id"],
            recipient_id=expected["recipient_id"],
            description=expected["description"],
            verb=expected["verb"],
            action_object_object_id=expected["action_object_object_id"],
        ).exists()
        self.assertTrue(is_existed)

    def test_post_update_by_other_teacher_with_send_notification(self):
        self.example.updated_by = self.other_experimental_user
        self.example.save()
        self.example.refresh_from_db()

        expected = {
            "sender_id": self.example.updated_by.id,
            "recipient_id": self.example.added_by.id,
            "description": _(
                "Your example {headline} is updated by Teacher {user_fullname}"
            ).format(
                headline=self.example.headline,
                user_fullname=self.other_experimental_user.full_name,
            ),
            "verb": constants.Activity.UPDATE_EXAMPLE,
            "action_object_object_id": self.example.id,
        }

        is_existed = Notification.objects.filter(
            actor_object_id=expected["sender_id"],
            recipient_id=expected["recipient_id"],
            verb=expected["verb"],
            description=expected["description"],
            action_object_object_id=expected["action_object_object_id"],
        ).exists()
        self.assertTrue(is_existed)

    # check send notification fail with none added_by and updated_by
    def test_post_update_signal_with_send_notification_fail_none_modifier(
        self,
    ):
        example = ExampleFactory.create(added_by=self.normal_user)
        old_updated_by = example.updated_by
        example.headline = "headline update"
        example.updated_by = None
        example.save()
        example.refresh_from_db()

        expected = {
            "sender_id": old_updated_by.id,
            "descriptions": [
                _("You just have updated example {headline}").format(
                    headline=example.headline
                ),
                _(
                    "Your example {headline} is updated by "
                    "Teacher {user_fullname}"
                ).format(
                    headline=example.headline,
                    user_fullname=self.other_experimental_user.full_name,
                ),
            ],
            "verb": constants.Activity.UPDATE_EXAMPLE,
            "action_object_object_id": self.example1.id,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=str(expected["sender_id"]),
            verb__in=[expected["descriptions"]],
            verb=expected["verb"],
            action_object_object_id=self.example1,
        ).exists()
        self.assertFalse(is_existed)

    def test_post_save_creation_with_tip_and_check_update_last_used_at(self):
        student_tip = StudentTipFactory.create()
        self.assertIsNone(student_tip.last_used_at)

        episode = EpisodeFactory.create(student=student_tip.student)
        ExampleFactory.create(tip=student_tip.tip, episode=episode)

        student_tip.refresh_from_db()
        self.assertIsNotNone(student_tip.last_used_at)

    def test_post_save_with_attach_tip_and_check_update_last_used_at(self):
        student_tip = StudentTipFactory.create()
        self.assertIsNone(student_tip.last_used_at)

        episode = EpisodeFactory.create(student=student_tip.student)

        example = ExampleFactory.create(episode=episode)

        student_tip.refresh_from_db()
        self.assertIsNone(student_tip.last_used_at)

        # check update something
        example.headline = "new headline"
        example.save()
        student_tip.refresh_from_db()
        self.assertIsNone(student_tip.last_used_at)

        # update tip
        example.tip = student_tip.tip
        example.save()

        student_tip.refresh_from_db()
        self.assertIsNotNone(student_tip.last_used_at)

    def test_post_save_with_add_new_tip_and_check_attach_tip_notifications(
        self,
    ):
        old_count = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient=self.admin_user,
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE,
        ).count()

        tip = TipFactory.create()
        ExampleFactory.create(
            tip=tip,
            added_by=self.admin_user,
            updated_by=None,
        )

        new_count = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient=self.admin_user,
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE,
        ).count()

        self.assertEqual(old_count + 1, new_count)

    def test_pre_save_with_update_tip_and_check_attach_tip_notifications(self):
        old_count = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient=self.admin_user,
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE,
        ).count()

        tip = TipFactory.create(added_by=self.normal_user)
        self.example.tip = tip
        self.example.updated_by = self.admin_user
        self.example.save()

        new_count = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient=self.admin_user,
            verb=constants.Activity.ATTACH_TIP_WITH_EXAMPLE,
        ).count()

        self.assertEqual(old_count + 1, new_count)

    def test_pre_save_with_check_detach_tip_notifications(self):
        count1 = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient=self.admin_user,
            verb=constants.Activity.DETACH_TIP_FROM_EXAMPLE,
        ).count()

        self.example.tip_id = None
        self.example.updated_by = self.admin_user
        self.example.save()

        count2 = Notification.objects.filter(
            actor_object_id=self.admin_user.id,
            recipient=self.admin_user,
            verb=constants.Activity.DETACH_TIP_FROM_EXAMPLE,
        ).count()

        self.assertEqual(count1 + 1, count2)
