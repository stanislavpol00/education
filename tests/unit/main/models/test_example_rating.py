from django.test import TestCase

from tests.factories import ExampleRatingFactory


class TestExampleRating(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.example_rating = ExampleRatingFactory.build(
            clarity=4, recommended=3
        )

    def test_stars(self):
        self.assertEqual(self.example_rating.stars, 3.5)
