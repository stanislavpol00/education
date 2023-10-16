from main.models import UserStudentMapping
from tests.base_test import BaseTestCase
from tests.factories import StudentFactory, UserStudentMappingFactory
from v1.serializers import AssignStudentSerializer, UnAssignStudentSerializer


class TestAssignStudentSerializer(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student1 = StudentFactory.create(nickname="student1")
        cls.student2 = StudentFactory.create(nickname="student2")
        cls.valid_data = {
            "students": [cls.student1.id, cls.student2.id],
            "practitioner": cls.experimental_user.id,
        }

        cls.invalid_data = {
            # students not exists
            "students": [12121, 23432],
            "practitioner": cls.experimental_user.id,
        }

    def test_is_valid_success(self):
        serializer = AssignStudentSerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid())

    def test_is_valid_fail(self):
        serializer = AssignStudentSerializer(data=self.invalid_data)

        self.assertFalse(serializer.is_valid())

    def test_save_success(self):
        fake_request = type("Request", (), {"user": self.manager_user})

        serializer = AssignStudentSerializer(
            data=self.valid_data, context={"request": fake_request}
        )
        serializer.is_valid()

        old_count = UserStudentMapping.objects.filter(
            user_id=self.experimental_user.id
        ).count()
        serializer.save()
        current_count = UserStudentMapping.objects.filter(
            user_id=self.experimental_user.id
        ).count()

        self.assertEqual(old_count + 2, current_count)

        serializer = AssignStudentSerializer(
            data=self.valid_data, context={"request": fake_request}
        )
        serializer.is_valid()
        serializer.save()
        new_count = UserStudentMapping.objects.filter(
            user_id=self.experimental_user.id
        ).count()
        self.assertEqual(current_count, new_count)


class TestUnAssignStudentSerializer(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student1 = StudentFactory.create(nickname="student1")
        cls.student2 = StudentFactory.create(nickname="student2")

        UserStudentMappingFactory.create(
            student=cls.student1,
            user=cls.experimental_user,
            added_by=cls.manager_user,
        )
        UserStudentMappingFactory.create(
            student=cls.student2,
            user=cls.experimental_user,
            added_by=cls.manager_user,
        )

        cls.valid_data = {
            "students": [cls.student1.id, cls.student2.id],
            "practitioner": cls.experimental_user.id,
        }

        cls.invalid_data = {
            # students not exists
            "students": [-1, -2],
            "practitioner": cls.experimental_user.id,
        }

    def test_is_valid_success(self):
        serializer = UnAssignStudentSerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid())

    def test_is_valid_fail(self):
        serializer = UnAssignStudentSerializer(data=self.invalid_data)

        self.assertFalse(serializer.is_valid())

    def test_save_success(self):
        serializer = UnAssignStudentSerializer(data=self.valid_data)
        serializer.is_valid()

        old_count = UserStudentMapping.objects.filter(
            user_id=self.experimental_user.id
        ).count()
        serializer.save()
        current_count = UserStudentMapping.objects.filter(
            user_id=self.experimental_user.id
        ).count()

        self.assertEqual(old_count - 2, current_count)

        serializer = UnAssignStudentSerializer(data=self.valid_data)
        serializer.is_valid()
        serializer.save()
        new_count = UserStudentMapping.objects.filter(
            user_id=self.experimental_user.id
        ).count()
        self.assertEqual(current_count, new_count)
