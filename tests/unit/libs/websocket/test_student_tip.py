from notifications.models import Notification

import constants
from libs.websocket import StudentTipNotificationWebsocket
from tests.base_test import BaseTestCase
from tests.factories import (
    StudentFactory,
    StudentTipFactory,
    UserStudentMappingFactory,
)


class TestStudentTipNotificationWebsocket(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student = StudentFactory.create()

        cls.student_tip1 = StudentTipFactory.create(
            student=cls.student,
            added_by=cls.manager_user,
        )
        cls.student_tip2 = StudentTipFactory.create(
            student=cls.student,
            added_by=cls.super_user,
        )

        UserStudentMappingFactory.create(
            user=cls.super_user,
            student=cls.student,
            added_by=cls.super_user,
        )

    def test_send_student_tip_notification_to_mapped_users(self):
        old_count = Notification.objects.filter(
            verb=constants.Activity.SUGGEST_TIP
        ).count()

        StudentTipNotificationWebsocket.send_student_tip_notification_to_mapped_users(  # noqa
            self.student_tip1
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.SUGGEST_TIP
        ).count()
        self.assertEqual(old_count + 1, new_count)

    def test_send_student_tip_notification_to_mapped_users_with_mapped_user_is_owner_student_tip(
        self,
    ):
        old_count = Notification.objects.filter(
            verb=constants.Activity.SUGGEST_TIP
        ).count()

        StudentTipNotificationWebsocket.send_student_tip_notification_to_mapped_users(  # noqa
            self.student_tip2
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.SUGGEST_TIP
        ).count()
        self.assertEqual(old_count, new_count)
