from tests.base_test import BaseTestCase
from tests.factories import StudentFactory
from v1.serializers import StudentActivitiesSerializer


class TestStudentActivitiesSerializer(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student = StudentFactory.create()

        cls.expected_keys = ["tips", "examples", "episodes"]

    def test_to_representation_check_keys(self):
        serializer = StudentActivitiesSerializer(self.student)
        self.assertListEqual(self.expected_keys, [*serializer.data])
