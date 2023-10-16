from tests.base_test import BaseTestCase
from tests.factories import UserStudentMappingFactory


class TestUserStudentMapping(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_student_mapping1 = UserStudentMappingFactory.build(
            user=cls.experimental_user, added_by=cls.manager_user
        )

        cls.user_student_mapping2 = UserStudentMappingFactory.build(
            user=cls.manager_user, added_by=cls.manager_user
        )

    def test_has_assigned_student_yourself(self):
        # False
        self.assertFalse(
            self.user_student_mapping1.has_assigned_student_yourself
        )

        # True
        self.assertTrue(
            self.user_student_mapping2.has_assigned_student_yourself
        )
