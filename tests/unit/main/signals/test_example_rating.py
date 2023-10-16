from notifications.models import Notification

import constants
from tests.base_test import BaseTestCase
from tests.factories import ExampleRatingFactory


class TestExampleRating(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.example_rating = ExampleRatingFactory.create(
            added_by=cls.experimental_user,
        )
        cls.example_rating1 = ExampleRatingFactory.create(
            added_by=None,
        )

    def test_post_save_by_teacher_check_send_notification(self):
        expected_owner_received = {
            "sender_id": self.example_rating.added_by.id,
            "recipient_id": self.example_rating.added_by.id,
            "description": "You have rated example {} {} stars".format(
                self.example_rating.example.headline, self.example_rating.stars
            ),
            "verb": constants.Activity.RATE_EXAMPLE,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_owner_received["sender_id"],
            recipient_id=expected_owner_received["recipient_id"],
            description=expected_owner_received["description"],
            verb=expected_owner_received["verb"],
        )
        self.assertTrue(is_existed)

        expected_manager_user_received = {
            "sender_id": self.example_rating.added_by.id,
            "recipient_id": self.manager_user.id,
            "description": "Teacher {} has rated example {} {} stars".format(
                self.example_rating.added_by.full_name,
                self.example_rating.example.headline,
                self.example_rating.stars,
            ),
            "verb": constants.Activity.RATE_EXAMPLE,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_manager_user_received["sender_id"],
            recipient_id=expected_manager_user_received["recipient_id"],
            description=expected_manager_user_received["description"],
            verb=expected_manager_user_received["verb"],
        )
        self.assertTrue(is_existed)

    # check send notification fail with none added_by
    def test_post_save_by_teacher_check_send_notification_fail(self):
        expected = {
            "sender_id": self.experimental_user.id,
            "description": [
                "You have rated example {} {} stars".format(
                    self.example_rating1.example.headline,
                    self.example_rating1.stars,
                )
            ],
            "verb": constants.Activity.RATE_EXAMPLE,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=str(expected["sender_id"]),
            verb=expected["verb"],
            description=expected["description"],
        )
        self.assertFalse(is_existed)
