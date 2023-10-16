from django.utils.translation import gettext as _
from notifications.models import Notification

import constants
from tests.base_test import BaseTestCase
from tests.factories import TipRatingFactory


class TestTipRating(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip_rating = TipRatingFactory.create(
            added_by=cls.experimental_user,
        )

    def test_post_save_by_teacher_check_send_notification(self):
        expected_owner_received = {
            "sender_id": self.tip_rating.added_by.id,
            "recipient_id": self.tip_rating.added_by.id,
            "description": _(
                "You have rated tip {title} {stars} stars"
            ).format(
                title=self.tip_rating.tip.title,
                stars=self.tip_rating.stars,
            ),
            "verb": constants.Activity.RATE_TIP,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_owner_received["sender_id"],
            recipient_id=expected_owner_received["recipient_id"],
            description=expected_owner_received["description"],
            verb=expected_owner_received["verb"],
        )
        self.assertTrue(is_existed)

        expected_manager_user_received = {
            "sender_id": self.tip_rating.added_by.id,
            "recipient_id": self.manager_user.id,
            "description": _(
                "Teacher {user_fullname} has rated tip {title} {stars} stars"
            ).format(
                user_fullname=self.tip_rating.added_by.full_name,
                title=self.tip_rating.tip.title,
                stars=self.tip_rating.stars,
            ),
            "verb": constants.Activity.RATE_TIP,
        }
        is_existed = Notification.objects.filter(
            actor_object_id=expected_manager_user_received["sender_id"],
            recipient_id=expected_manager_user_received["recipient_id"],
            description=expected_manager_user_received["description"],
            verb=expected_manager_user_received["verb"],
        )
        self.assertTrue(is_existed)
