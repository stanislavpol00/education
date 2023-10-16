from notifications.models import Notification

import constants
from tests.base_test import BaseTestCase
from tests.factories import (
    StudentFactory,
    StudentTipFactory,
    TipFactory,
    UserStudentMappingFactory,
)


class TestStudent(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = StudentFactory.create(
            added_by=cls.experimental_user,
        )

        cls.student1 = StudentFactory.create()
        cls.student2 = StudentFactory.create()

        cls.tip1 = TipFactory.create()
        cls.tip2 = TipFactory.create()

        cls.student_tip1 = StudentTipFactory.create(
            student=cls.student1, tip=cls.tip1
        )
        cls.student_tip2 = StudentTipFactory.create(
            student=cls.student1, tip=cls.tip2
        )
        cls.student_tip3 = StudentTipFactory.create(
            student=cls.student2, tip=cls.tip1
        )
        cls.student_tip4 = StudentTipFactory.create(
            student=cls.student2, tip=cls.tip2
        )

        cls.user_student_mapping1 = UserStudentMappingFactory.create(
            user=cls.experimental_user,
            student=cls.student1,
            added_by=cls.manager_user,
        )
        cls.user_student_mapping2 = UserStudentMappingFactory.create(
            user=cls.experimental_user,
            student=cls.student2,
            added_by=cls.manager_user,
        )
        cls.user_student_mapping3 = UserStudentMappingFactory.create(
            user=cls.manager_user,
            student=cls.student1,
            added_by=cls.super_user,
        )

    def test_post_save_by_teacher_check_send_notification(self):
        expected = {
            "sender_id": self.student.added_by.id,
            "recipient_id": self.manager_user.id,
            "description": "A new student {} is created by teacher {}".format(
                self.student.full_name,
                self.experimental_user.full_name,
            ),
            "verb": constants.Activity.CREATE_STUDENT,
        }

        is_existed = Notification.objects.filter(
            actor_object_id=expected["sender_id"],
            recipient_id=expected["recipient_id"],
            description=expected["description"],
            verb=expected["verb"],
        )
        self.assertTrue(is_existed)

    def test_post_save_send_notification_fail_with_none_added_by(self):
        StudentFactory.create(added_by=None)

        count = Notification.objects.filter(
            recipient_id=self.manager_user.id
        ).count()
        self.assertNotEqual(count, 2)
