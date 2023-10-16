import constants
from tests.base_test import BaseTestCase
from tests.factories import StudentFactory, StudentTipFactory


class TestStudentTipNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = StudentFactory.build(added_by=cls.experimental_user)
        cls.student_tip = StudentTipFactory.build(student=cls.student)

    def test_generate_creation_notification_by_experimental_user(self):
        expected = {
            "sender": self.student_tip.added_by,
            "recipient": self.student_tip.student.added_by,
            "description": "A tip {} is assigned to your student {}".format(
                self.student_tip.tip.title,
                self.student_tip.student.full_name,
            ),
            "verb": constants.Activity.ASSIGN_TIP_TO_STUDENT,
            "action_object": self.student_tip.tip,
            "target": self.student,
        }
        actual = self.student_tip.generate_student_tip_creation_notification()

        self.assertEqual(expected["sender"], actual[0]["sender"])
        self.assertEqual(expected["recipient"], actual[0]["recipient"])
        self.assertEqual(expected["description"], actual[0]["description"])
        self.assertEqual(expected["action_object"], actual[0]["action_object"])
        self.assertEqual(expected["target"], actual[0]["target"])

    def test_generate_creation_notification_fail_with_none_added_by(self):
        self.student.added_by = None

        expected = []
        actual = self.student_tip.generate_student_tip_creation_notification()

        self.assertEqual(actual, expected)
