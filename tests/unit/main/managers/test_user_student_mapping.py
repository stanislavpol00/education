from main.models import UserStudentMapping
from tests.base_test import BaseTestCase
from tests.factories import StudentFactory, UserStudentMappingFactory


class TestUserStudentTip(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student1 = StudentFactory.create()
        cls.student2 = StudentFactory.create()

        cls.user_student_mapping1 = UserStudentMappingFactory.create(
            user=cls.normal_user,
            student=cls.student1,
            added_by=cls.manager_user,
        )
        cls.user_student_mapping2 = UserStudentMappingFactory.create(
            user=cls.normal_user,
            student=cls.student2,
            added_by=cls.manager_user,
        )
        cls.user_student_mapping3 = UserStudentMappingFactory.create(
            user=cls.manager_user,
            student=cls.student1,
            added_by=cls.manager_user,
        )

    def test_get_users_students_dictionary(self):
        user_ids = [self.normal_user.id, self.manager_user.id]

        user_student_dictionary = (
            UserStudentMapping.objects.get_users_students_dictionary(
                user_ids=user_ids
            )
        )

        self.assertIn(self.normal_user.id, user_student_dictionary)
        self.assertListEqual(
            [self.student1.id, self.student2.id],
            user_student_dictionary[self.normal_user.id],
        )

        self.assertIn(self.manager_user.id, user_student_dictionary)
        self.assertListEqual(
            [self.student1.id], user_student_dictionary[self.manager_user.id]
        )

    def test_get_students(self):
        # user = normal_user
        student_ids = UserStudentMapping.objects.get_students(
            user_id=self.normal_user.id
        )

        self.assertQuerysetEqual(
            student_ids, [self.student1.id, self.student2.id], ordered=False
        )

        # user = manager_user
        student_ids = UserStudentMapping.objects.get_students(
            user_id=self.manager_user.id
        )

        self.assertQuerysetEqual(student_ids, [self.student1.id])
