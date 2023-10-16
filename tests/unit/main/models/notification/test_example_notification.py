from django.utils.translation import gettext as _

import constants
from tests.base_test import BaseTestCase
from tests.factories import ExampleFactory


class TestExampleNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.example = ExampleFactory.build(
            headline="example headline",
            added_by=cls.experimental_user,
        )

    def test_generate_creation_notification_success(self):
        expected = [
            {
                "sender": self.example.added_by,
                "recipient": self.example.added_by,
                "description": _(
                    "You have created a new example {headline}"
                ).format(
                    headline=self.example.headline,
                ),
                "verb": constants.Activity.CREATE_EXAMPLE,
                "action_object": self.example,
            },
            {
                "sender": self.example.added_by,
                "recipient": [self.admin_user, self.manager_user],
                "description": _(
                    "Teacher {user_fullname} has created "
                    "a new example {headline}"
                ).format(
                    user_fullname=self.example.added_by.full_name,
                    headline=self.example.headline,
                ),
                "verb": constants.Activity.CREATE_EXAMPLE,
                "action_object": self.example,
            },
        ]

        actual = self.example.generate_example_creation_notification()

        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )

        self.assertEqual(expected[1]["sender"], actual[1]["sender"])
        recipients = list(actual[1]["recipient"])
        self.assertEqual(len(recipients), len(expected[1]["recipient"]))
        self.assertIn(recipients[0], expected[1]["recipient"])
        self.assertIn(recipients[1], expected[1]["recipient"])
        self.assertEqual(expected[1]["description"], actual[1]["description"])
        self.assertEqual(
            expected[1]["action_object"], actual[1]["action_object"]
        )

    def test_generate_creation_notification_with_none_added_by(self):
        self.example.added_by = None

        expected = []
        actual = self.example.generate_example_creation_notification()

        self.assertEqual(actual, expected)

    def test_generate_updating_notification_by_other_teacher(self):
        self.example.updated_by = self.other_experimental_user
        expected = [
            {
                "sender": self.example.updated_by,
                "recipient": self.example.updated_by,
                "description": _(
                    "You just have updated example {headline}"
                ).format(
                    headline=self.example.headline,
                ),
                "verb": constants.Activity.UPDATE_EXAMPLE,
                "action_object": self.example,
            },
            {
                "sender": self.example.updated_by,
                "recipient": self.example.added_by,
                "description": _(
                    "Your example {headline} is updated by "
                    "Teacher {user_fullname}"
                ).format(
                    headline=self.example.headline,
                    user_fullname=self.other_experimental_user.full_name,
                ),
                "verb": constants.Activity.UPDATE_EXAMPLE,
                "action_object": self.example,
            },
        ]

        actual = self.example.generate_example_updating_notification()
        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )

        self.assertEqual(expected[1]["sender"], actual[1]["sender"])
        self.assertEqual(expected[1]["recipient"], actual[1]["recipient"])
        self.assertEqual(expected[1]["description"], actual[1]["description"])
        self.assertEqual(
            expected[1]["action_object"], actual[1]["action_object"]
        )

    def test_generate_updating_notification_by_owner(self):
        self.example.updated_by = self.experimental_user
        expected = {
            "sender": self.example.updated_by,
            "recipient": self.example.added_by,
            "description": _(
                "You just have updated example {headline}"
            ).format(headline=self.example.headline),
            "verb": constants.Activity.UPDATE_EXAMPLE,
            "action_object": self.example,
        }

        actual = self.example.generate_example_updating_notification()
        self.assertEqual(expected["sender"], actual[0]["sender"])
        self.assertEqual(expected["recipient"], actual[0]["recipient"])
        self.assertEqual(expected["description"], actual[0]["description"])
        self.assertEqual(expected["action_object"], actual[0]["action_object"])

    def test_generate_updating_notification_fail_with_none_added_by(self):
        self.example.added_by = None
        self.example.updated_by = self.other_experimental_user

        expected = []
        actual = self.example.generate_example_updating_notification()

        self.assertEqual(actual, expected)

    def test_generate_updating_notification_fail_with_none_updated_by(self):
        self.example.updated_by = None

        expected = []
        actual = self.example.generate_example_updating_notification()

        self.assertEqual(actual, expected)
