import constants
from tests.base_test import BaseTestCase
from tests.factories import TipFactory


class TestTipNotification(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip = TipFactory.build(
            title="tip title",
            added_by=cls.experimental_user,
        )

    def test_generate_creation_notification_success(self):
        expected = [
            {
                "sender": self.tip.added_by,
                "recipient": self.tip.added_by,
                "description": "You have created a new tip {}".format(
                    self.tip.title,
                ),
                "verb": constants.Activity.CREATE_TIP,
                "action_object": self.tip,
            },
            {
                "sender": self.tip.added_by,
                "recipient": [self.admin_user, self.manager_user],
                "description": "Teacher {} has created a new tip {}".format(
                    self.tip.added_by.full_name,
                    self.tip.title,
                ),
                "verb": constants.Activity.CREATE_TIP,
                "action_object": self.tip,
            },
        ]

        actual = self.tip.generate_tip_creation_notification()

        self.assertEqual(expected[0]["sender"], actual[0]["sender"])
        self.assertEqual(expected[0]["recipient"], actual[0]["recipient"])
        self.assertEqual(expected[0]["description"], actual[0]["description"])
        self.assertEqual(
            expected[0]["action_object"], actual[0]["action_object"]
        )

        self.assertEqual(expected[1]["sender"], actual[1]["sender"])
        recipients = list(actual[1]["recipient"])
        self.assertEqual(
            expected[1]["recipient"],
            recipients,
        )
        self.assertEqual(expected[1]["description"], actual[1]["description"])
        self.assertEqual(
            expected[1]["action_object"], actual[1]["action_object"]
        )

    def test_generate_creation_notification_with_none_added_by(self):
        self.tip.added_by = None

        expected = []
        actual = self.tip.generate_tip_creation_notification()

        self.assertEqual(actual, expected)

    def test_generate_updating_notification_by_other_teacher(self):
        self.tip.updated_by = self.other_experimental_user
        expected = [
            {
                "sender": self.tip.updated_by,
                "recipient": self.tip.updated_by,
                "description": "You just have updated tip {}".format(
                    self.tip.title,
                ),
                "verb": constants.Activity.UPDATE_TIP,
                "action_object": self.tip,
            },
            {
                "sender": self.tip.updated_by,
                "recipient": self.tip.added_by,
                "description": "Your tip {} is updated by Teacher {}".format(
                    self.tip.title,
                    self.other_experimental_user.full_name,
                ),
                "verb": constants.Activity.UPDATE_TIP,
                "action_object": self.tip,
            },
        ]

        actual = self.tip.generate_tip_updating_notification()
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
        self.tip.updated_by = self.experimental_user
        expected = {
            "sender": self.tip.updated_by,
            "recipient": self.tip.added_by,
            "description": "You just have updated tip {}".format(
                self.tip.title
            ),
            "verb": constants.Activity.UPDATE_TIP,
            "action_object": self.tip,
        }

        actual = self.tip.generate_tip_updating_notification()
        self.assertEqual(expected["sender"], actual[0]["sender"])
        self.assertEqual(expected["recipient"], actual[0]["recipient"])
        self.assertEqual(expected["description"], actual[0]["description"])
        self.assertEqual(expected["action_object"], actual[0]["action_object"])

    def test_generate_updating_notification_fail_with_none_added_by(self):
        self.tip.added_by = None
        self.tip.updated_by = self.other_experimental_user

        expected = []
        actual = self.tip.generate_tip_updating_notification()

        self.assertEqual(actual, expected)

    def test_generate_updating_notification_fail_with_none_updated_by(self):
        self.tip.updated_by = None

        expected = []
        actual = self.tip.generate_tip_updating_notification()

        self.assertEqual(actual, expected)
