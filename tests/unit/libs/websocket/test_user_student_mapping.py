from notifications.models import Notification

import constants
from libs.websocket import UserStudentMappingNotificationWebsocket
from tests.base_test import BaseTestCase
from tests.factories import UserStudentMappingFactory


class TestUserStudentMappingNotificationWebsocket(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_student1 = UserStudentMappingFactory.create(
            user=cls.manager_user,
            added_by=cls.manager_user,
        )

        cls.user_student2 = UserStudentMappingFactory.create(
            user=cls.manager_user,
            added_by=cls.super_user,
        )

    def test_send_assign_student_notification_to_mapped_user(self):
        # self.user_student1.added_by_id == self.user_student1.user_id
        old_count = Notification.objects.filter(
            verb=constants.Activity.ASSIGN_STUDENT
        ).count()

        UserStudentMappingNotificationWebsocket.send_assign_student_notification_to_mapped_user(
            self.user_student1
        )

        count = Notification.objects.filter(
            verb=constants.Activity.ASSIGN_STUDENT
        ).count()
        self.assertEqual(old_count, count)

        # self.user_student2.added_by_id != self.user_student2.user_id
        old_count = Notification.objects.filter(
            verb=constants.Activity.ASSIGN_STUDENT
        ).count()

        UserStudentMappingNotificationWebsocket.send_assign_student_notification_to_mapped_user(
            self.user_student2
        )

        count = Notification.objects.filter(
            verb=constants.Activity.ASSIGN_STUDENT
        ).count()
        self.assertEqual(old_count + 1, count)
