import constants
from main.models import StudentTip
from tasks.student_tip import dequeue_student_tips
from tests.base_test import BaseTestCase
from tests.factories import (
    StudentFactory,
    StudentTipFactory,
    TipFactory,
    UserFactory,
)


class TestStudentTipTask(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Assign tip
        cls.tip1 = TipFactory.create()
        cls.tip2 = TipFactory.create()
        cls.tip3 = TipFactory.create()

        cls.student1 = StudentFactory.create()
        cls.student2 = StudentFactory.create()

        cls.another_experimental_user = UserFactory.create(
            role=constants.Role.EXPERIMENTAL_TEACHER
        )

        StudentTipFactory.create(
            tip=cls.tip1, student=cls.student1, is_queued=True
        )
        StudentTipFactory.create(
            tip=cls.tip2, student=cls.student1, is_queued=True
        )
        StudentTipFactory.create(
            tip=cls.tip3, student=cls.student1, is_queued=True
        )

        StudentTipFactory.create(
            tip=cls.tip1, student=cls.student2, is_queued=True
        )
        StudentTipFactory.create(
            tip=cls.tip2, student=cls.student2, is_queued=True
        )

    def test_dequeue_student_tips(self):
        old_count = StudentTip.objects.filter(is_queued=True).count()

        # first call
        dequeue_student_tips(number_of_tips=2)

        new_count = StudentTip.objects.filter(is_queued=True).count()
        self.assertEqual(old_count - 4, new_count)
