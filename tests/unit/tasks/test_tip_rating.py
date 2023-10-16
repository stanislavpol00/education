from notifications.models import Notification

import constants
from tasks.tip_rating import rating_reminder
from tests.base_test import BaseTestCase
from tests.factories import TipRatingFactory, UserFactory


class TestTipRatingTasks(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create(role=constants.Role.EDUCATOR_SHADOW)

        TipRatingFactory.create(
            clarity=0,
            relevance=0,
            uniqueness=0,
            read_count=0,
            added_by=cls.user,
        )
        TipRatingFactory.create(
            clarity=0,
            relevance=0,
            uniqueness=1,
            read_count=1,
            added_by=cls.user,
        )
        TipRatingFactory.create(
            clarity=0,
            relevance=0,
            uniqueness=0,
            read_count=1,
            added_by=cls.user,
        )

    def test_rating_reminder(self):
        rating_reminder()

        expected_tip_read_but_not_rated_count = 1

        is_existed = Notification.objects.filter(
            verb=constants.Activity.RATING_REMINDER,
            description="You have {} tips awaiting your review.".format(
                expected_tip_read_but_not_rated_count
            ),
            actor_object_id=self.user.id,
            recipient=self.user,
        ).exists()

        self.assertTrue(is_existed)
