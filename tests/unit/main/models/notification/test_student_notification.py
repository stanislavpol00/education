import constants
from tests.base_test import BaseTestCase
from tests.factories import StudentFactory


class TestStudentNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student = StudentFactory.build(
            first_name="harry",
            last_name="kane",
            added_by=cls.experimental_user,
        )

    def test_generate_student_creation_notification_by_experimental_user(self):
        expected = [
            {
                "sender": self.student.added_by,
                "recipient": self.experimental_user,
                "description": "You have added a new student {}".format(
                    self.student.full_name,
                ),
                "verb": constants.Activity.CREATE_STUDENT,
                "action_object": self.student,
            },
            {
                "sender": self.student.added_by,
                "recipient": [self.admin_user, self.manager_user],
                "description": "A new student {} is created by teacher {}".format(
                    self.student.full_name,
                    self.student.added_by.full_name,
                ),
                "verb": constants.Activity.CREATE_STUDENT,
                "action_object": self.student,
            },
        ]
        actual = self.student.generate_student_creation_notification()

        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(
            expected[0]["recipient"],
            actual[0]["recipient"],
        )
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )

        recipients = list(actual[1]["recipient"])
        self.assertEqual(len(recipients), len(expected[1]["recipient"]))
        self.assertIn(recipients[0], expected[1]["recipient"])
        self.assertIn(recipients[1], expected[1]["recipient"])
        self.assertEqual(expected[1]["description"], actual[1]["description"])
        self.assertEqual(
            expected[1]["action_object"], actual[1]["action_object"]
        )

    def test_generate_creation_notification_fail_with_none_added_by(self):
        self.student.added_by = None

        expected = []
        actual = self.student.generate_student_creation_notification()

        self.assertEqual(actual, expected)
