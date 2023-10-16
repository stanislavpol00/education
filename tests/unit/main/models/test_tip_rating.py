from django.test import TestCase

from tests.factories import TipRatingFactory


class TestTipRating(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip_rating = TipRatingFactory.build(
            clarity=4, relevance=5, uniqueness=3
        )

    def test_stars(self):
        self.assertEqual(self.tip_rating.stars, 4)
