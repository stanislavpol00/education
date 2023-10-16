from notifications.models import Notification

import constants
from tests.base_test import BaseTestCase
from tests.factories import (
    StudentFactory,
    StudentTipFactory,
    TipFactory,
    UserStudentMappingFactory,
)


class TestStudentTip(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student_tip = StudentTipFactory.create()

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
            "sender_id": self.student_tip.added_by.id,
            "recipient_id": self.student_tip.student.added_by.id,
            "description": "A tip {} is assigned to your student {}".format(
                self.student_tip.tip.title, self.student_tip.student.full_name
            ),
            "verb": constants.Activity.ASSIGN_TIP_TO_STUDENT,
        }

        is_existed = Notification.objects.filter(
            actor_object_id=expected["sender_id"],
            recipient_id=expected["recipient_id"],
            description=expected["description"],
            verb=expected["verb"],
        )
        self.assertTrue(is_existed)

    def test_post_save_send_notification_fail_with_none_added_by(self):
        student = StudentFactory.create(added_by=None)
        student_tip = StudentTipFactory.create(student=student)
        expected_description = (
            "A tip {} is assigned to your student {}".format(
                student_tip.tip.title, student_tip.student.full_name
            )
        )
        expected_verb = constants.Activity.ASSIGN_TIP_TO_STUDENT
        is_existed = Notification.objects.filter(
            description=expected_description, verb=expected_verb
        ).exists()
        self.assertFalse(is_existed)
