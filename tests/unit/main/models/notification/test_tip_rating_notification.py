from django.utils.translation import gettext as _

import constants
from tests.base_test import BaseTestCase
from tests.factories import TipFactory, TipRatingFactory


class TestTipRatingNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.tip = TipFactory.build(
            title="tip by normal user",
        )
        cls.tip_rating = TipRatingFactory.build(
            tip=cls.tip, added_by=cls.normal_user
        )

    def test_generate_creation_notification(self):
        expected = [
            {
                "sender": self.tip_rating.added_by,
                "recipient": self.tip_rating.added_by,
                "description": _(
                    "You have rated tip {title} {stars} stars"
                ).format(
                    title=self.tip.title,
                    stars=self.tip_rating.stars,
                ),
                "verb": constants.Activity.RATE_TIP,
                "action_object": self.tip_rating.tip,
                "target": self.tip_rating,
            },
            {
                "sender": self.tip_rating.added_by,
                "recipient": [self.admin_user, self.manager_user],
                "description": _(
                    "Teacher {user_fullname} has rated tip "
                    "{title} {stars} stars"
                ).format(
                    user_fullname=self.normal_user.full_name,
                    title=self.tip.title,
                    stars=self.tip_rating.stars,
                ),
                "verb": constants.Activity.RATE_TIP,
                "action_object": self.tip_rating.tip,
                "target": self.tip_rating,
            },
        ]
        actual = self.tip_rating.generate_tip_rating_creation_notification()
        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
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
        self.assertEqual(
            expected[1]["action_object"], actual[1]["action_object"]
        )
        self.assertEqual(expected[1]["target"], actual[1]["target"])

    def test_generate_read_tip_rating_notification(self):
        expected = [
            {
                "sender": self.tip_rating.added_by,
                "recipient": self.tip_rating.added_by,
                "description": _(
                    "{user_fullname} read the tip {title}"
                ).format(
                    user_fullname=self.tip_rating.added_by.full_name,
                    title=self.tip_rating.tip.title,
                ),
                "verb": constants.Activity.READ_TIP,
                "action_object": self.tip_rating.tip,
                "target": self.tip_rating,
                "level": "success",
            }
        ]
        actual = self.tip_rating.generate_read_tip_rating_notification()
        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )
        self.assertEqual(expected[0]["target"], actual[0]["target"])

    def test_generate_try_tip_rating_notification(self):
        expected = [
            {
                "sender": self.tip_rating.added_by,
                "recipient": self.tip_rating.added_by,
                "description": _(
                    "{user_fullname} tried the tip {title}"
                ).format(
                    user_fullname=self.tip_rating.added_by.full_name,
                    title=self.tip_rating.tip.title,
                ),
                "verb": constants.Activity.TRY_TIP,
                "action_object": self.tip_rating.tip,
                "target": self.tip_rating,
                "level": "success",
            }
        ]
        actual = self.tip_rating.generate_try_tip_rating_notification()
        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )
        self.assertEqual(expected[0]["target"], actual[0]["target"])

    def test_generate_comment_tip_rating_notification(self):
        expected = [
            {
                "sender": self.tip_rating.added_by,
                "recipient": self.tip_rating.added_by,
                "description": _(
                    "{user_fullname} commented the tip {title}"
                ).format(
                    user_fullname=self.tip_rating.added_by.full_name,
                    title=self.tip_rating.tip.title,
                ),
                "verb": constants.Activity.COMMENT_TIP,
                "action_object": self.tip_rating.tip,
                "target": self.tip_rating,
                "level": "success",
            }
        ]
        actual = self.tip_rating.generate_comment_tip_rating_notification()
        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )
        self.assertEqual(expected[0]["target"], actual[0]["target"])
