from tests.base_test import BaseTestCase
from tests.factories import (
    StudentFactory,
    StudentTipFactory,
    TipFactory,
    UserStudentMappingFactory,
)


class TestStudentExample(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

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
            added_by=cls.manager_user,
        )
