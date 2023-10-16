from main.models import Example, StudentExample
from tests.base_test import BaseTestCase
from tests.factories import (
    ExampleFactory,
    ExampleRatingFactory,
    StudentExampleFactory,
)


class TestExample(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.example = ExampleFactory.create()

    def test_updated_by_username(self):
        self.assertEqual(
            self.example.updated_by.username, self.example.updated_by_username
        )

    def test_average_ratings(self):
        example = ExampleFactory.create()

        ExampleRatingFactory.create(example=example, clarity=4, recommended=4)
        ExampleRatingFactory.create(example=example, clarity=2, recommended=2)
        expected_average_rating = 3

        average_ratings = example.average_ratings
        self.assertEqual(
            expected_average_rating, average_ratings["clarity_average_rating"]
        )
        self.assertEqual(
            expected_average_rating,
            average_ratings["recommended_average_rating"],
        )
        self.assertEqual(
            expected_average_rating, average_ratings["average_rating"]
        )

    def test_clarity_average_rating(self):
        example = ExampleFactory.create()

        self.assertIsNone(example.clarity_average_rating)

        ExampleRatingFactory.create(example=example, clarity=4, recommended=4)
        ExampleRatingFactory.create(example=example, clarity=2, recommended=2)

        example = Example.objects.get(id=example.id)
        self.assertEqual(3, example.clarity_average_rating)

    def test_recommended_average_rating(self):
        example = ExampleFactory.create()

        self.assertIsNone(example.recommended_average_rating)

        ExampleRatingFactory.create(example=example, clarity=4, recommended=4)
        ExampleRatingFactory.create(example=example, clarity=2, recommended=2)

        example = Example.objects.get(id=example.id)
        self.assertEqual(3, example.recommended_average_rating)

    def test_average_rating(self):
        example = ExampleFactory.create()

        self.assertIsNone(example.average_rating)

        ExampleRatingFactory.create(example=example, clarity=4, recommended=4)
        ExampleRatingFactory.create(example=example, clarity=2, recommended=2)

        example = Example.objects.get(id=example.id)
        self.assertEqual(3, example.average_rating)

    def test_episode_student_id(self):
        self.assertEqual(
            self.example.episode.student_id,
            self.example.episode_student_id,
        )

    def test_student_ids(self):
        StudentExampleFactory.create_batch(
            5,
            example=self.example,
        )
        expect_student_ids = [
            student_example.student_id
            for student_example in StudentExample.objects.filter(
                example=self.example
            )
        ]

        self.assertEqual(expect_student_ids, self.example.student_ids)
