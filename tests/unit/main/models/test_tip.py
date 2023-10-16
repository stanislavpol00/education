from unittest import mock

import constants
from main.models import Tip
from tests.base_test import BaseTestCase
from tests.factories import TipFactory, TipRatingFactory


class TestTip(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip = TipFactory.create(
            title="tip 1",
            description="description 1",
        )
        cls.tip1 = TipFactory.build(
            title="tip 2",
            description="description 2",
            added_by=cls.experimental_user,
            updated_by=None,
        )

    def test_updated_by_username(self):
        self.assertEqual(
            self.tip.updated_by.username, self.tip.updated_by_username
        )

    def test_str(self):
        str_tip = str(self.tip)

        self.assertEqual("Tip: %s" % self.tip.title, str_tip)

    def test_average_ratings(self):
        tip = TipFactory.create()

        TipRatingFactory.create(tip=tip, clarity=4, relevance=4, uniqueness=4)
        TipRatingFactory.create(tip=tip, clarity=2, relevance=2, uniqueness=2)
        expected_average_rating = 3

        average_ratings = tip.average_ratings
        self.assertEqual(
            expected_average_rating, average_ratings["clarity_average_rating"]
        )
        self.assertEqual(
            expected_average_rating,
            average_ratings["relevance_average_rating"],
        )
        self.assertEqual(
            expected_average_rating,
            average_ratings["uniqueness_average_rating"],
        )
        self.assertEqual(
            expected_average_rating, average_ratings["average_rating"]
        )

    def test_clarity_average_rating(self):
        tip = TipFactory.create()

        self.assertIsNone(tip.clarity_average_rating)

        TipRatingFactory.create(tip=tip, clarity=4, relevance=4, uniqueness=4)
        TipRatingFactory.create(tip=tip, clarity=2, relevance=2, uniqueness=2)

        tip = Tip.objects.get(id=tip.id)
        self.assertEqual(3, tip.clarity_average_rating)

    def test_relevance_average_rating(self):
        tip = TipFactory.create()

        self.assertIsNone(tip.relevance_average_rating)

        TipRatingFactory.create(tip=tip, clarity=4, relevance=4, uniqueness=4)
        TipRatingFactory.create(tip=tip, clarity=2, relevance=2, uniqueness=2)

        tip = Tip.objects.get(id=tip.id)
        self.assertEqual(3, tip.relevance_average_rating)

    def test_uniqueness_average_rating(self):
        tip = TipFactory.create()

        self.assertIsNone(tip.uniqueness_average_rating)

        TipRatingFactory.create(tip=tip, clarity=4, relevance=4, uniqueness=4)
        TipRatingFactory.create(tip=tip, clarity=2, relevance=2, uniqueness=2)

        tip = Tip.objects.get(id=tip.id)
        self.assertEqual(3, tip.uniqueness_average_rating)

    def test_average_rating(self):
        tip = TipFactory.create()

        self.assertIsNone(tip.average_rating)

        TipRatingFactory.create(tip=tip, clarity=4, relevance=4, uniqueness=4)
        TipRatingFactory.create(tip=tip, clarity=2, relevance=2, uniqueness=2)

        tip = Tip.objects.get(id=tip.id)
        self.assertEqual(3, tip.average_rating)

    def test_auto_update_context_flattened_fields(self):
        tip = TipFactory.create()
        tip.child_context = {
            constants.ChildContext.CURRENT_MOTIVATOR: {
                "order": 2,
                "value": "1",
            },
            constants.ChildContext.ANTICIPATED_MOTIVATOR: {
                "order": 1,
                "value": "2",
            },
            constants.ChildContext.CURRENT_BEHAVIOR: {
                "order": 3,
                "value": "3",
            },
            constants.ChildContext.ANTICIPATED_BEHAVIOR: {
                "order": 4,
                "value": "4",
            },
        }
        tip.environment_context = {
            constants.Environment.SPACE_OPPORTUNITIES: "2",
            constants.Environment.ACTIVITY_OPPORTUNITIES: "3",
            constants.Environment.COMMUNITY_ADULT_OPPORTUNITIES: "1",
            constants.Environment.PEER_OPPORTUNITIES: "4",
        }

        self.assertEqual(None, tip.child_context_flattened)
        self.assertEqual(None, tip.environment_context_flattened)

        tip.auto_update_context_flattened_fields()

        self.assertEqual("2\n1\n3", tip.child_context_flattened)
        self.assertEqual("2\n3\n1", tip.environment_context_flattened)

    @mock.patch.object(Tip, "auto_update_context_flattened_fields")
    def test_save_with_mock(self, mock_auto_update):
        TipFactory.create()

        self.assertEqual(1, mock_auto_update.call_count)
