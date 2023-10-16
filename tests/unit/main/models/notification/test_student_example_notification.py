import constants
from tests.base_test import BaseTestCase
from tests.factories import StudentExampleFactory, StudentFactory


class TestStudentExampleNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = StudentFactory.build(added_by=cls.experimental_user)
        cls.student_example = StudentExampleFactory.build(student=cls.student)

    def test_generate_student_example_creation_notification(
        self,
    ):
        expected = {
            "sender": self.student_example.added_by,
            "recipient": self.student_example.student.added_by,
            "description": "A example {} is assigned to your student {}".format(
                self.student_example.example.headline,
                self.student_example.student.full_name,
            ),
            "verb": constants.Activity.ASSIGN_EXAMPLE_TO_STUDENT,
            "action_object": self.student_example.example,
            "target": self.student,
        }
        actual = (
            self.student_example.generate_student_example_creation_notification()
        )

        self.assertEqual(expected["sender"], actual[0]["sender"])
        self.assertEqual(expected["recipient"], actual[0]["recipient"])
        self.assertEqual(expected["description"], actual[0]["description"])
        self.assertEqual(expected["action_object"], actual[0]["action_object"])
        self.assertEqual(expected["target"], actual[0]["target"])

    def test_generate_creation_notification_fail_with_none_added_by(self):
        self.student.added_by = None

        expected = []
        actual = (
            self.student_example.generate_student_example_creation_notification()
        )

        self.assertEqual(actual, expected)
