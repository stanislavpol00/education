from django.utils.translation import gettext as _

import constants
from tests.base_test import BaseTestCase
from tests.factories import ExampleFactory, ExampleRatingFactory


class TestExampleRatingNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.example = ExampleFactory.build(
            headline="example by normal user",
        )
        cls.example_rating = ExampleRatingFactory.build(
            example=cls.example, added_by=cls.normal_user
        )

    def test_generate_creation_notification_success(self):
        expected = [
            {
                "sender": self.example_rating.added_by,
                "recipient": self.example_rating.added_by,
                "description": _(
                    "You have rated example {headline} {stars} stars"
                ).format(
                    headline=self.example.headline,
                    stars=self.example_rating.stars,
                ),
                "verb": constants.Activity.RATE_EXAMPLE,
                "action_object": self.example_rating.example,
                "target": self.example_rating,
            },
            {
                "sender": self.example_rating.added_by,
                "recipient": [self.admin_user, self.manager_user],
                "description": _(
                    "Teacher {user_fullname} has rated example "
                    "{headline} {stars} stars"
                ).format(
                    user_fullname=self.normal_user.full_name,
                    headline=self.example.headline,
                    stars=self.example_rating.stars,
                ),
                "verb": constants.Activity.RATE_EXAMPLE,
                "action_object": self.example_rating.example,
                "target": self.example_rating,
            },
        ]
        actual = (
            self.example_rating.generate_example_rating_creation_notification()
        )
        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(expected[0]["verb"], actual[0]["verb"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )
        self.assertEqual(expected[0]["target"], actual[0]["target"])

        self.assertEqual(expected[1]["sender"], actual[1]["sender"])
        recipients = list(actual[1]["recipient"])
        self.assertEqual(len(recipients), len(expected[1]["recipient"]))
        self.assertIn(recipients[0], expected[1]["recipient"])
        self.assertIn(recipients[1], expected[1]["recipient"])
        self.assertEqual(expected[1]["description"], actual[1]["description"])
        self.assertEqual(expected[1]["verb"], actual[1]["verb"])
        self.assertEqual(
            expected[1]["action_object"], actual[1]["action_object"]
        )
        self.assertEqual(expected[1]["target"], actual[1]["target"])

    def test_generate_creation_notification_fail_with_none_added_by(self):
        self.example_rating.added_by = None

        expected = []
        actual = (
            self.example_rating.generate_example_rating_creation_notification()
        )

        self.assertEqual(actual, expected)
