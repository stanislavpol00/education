from main.models import TipRating
from tests.base_test import BaseTestCase
from tests.factories import StudentFactory, TipFactory, TipRatingFactory


class TestTipRating(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip = TipFactory.create()

        cls.student = StudentFactory.create()

        cls.tip_rating = TipRatingFactory.create(
            added_by=cls.normal_user,
            tip=cls.tip,
            clarity=0,
            relevance=0,
            uniqueness=0,
            read_count=0,
        )

        cls.tip_rating1 = TipRatingFactory.create(
            added_by=cls.normal_user,
            tip=cls.tip,
            student=cls.student,
            clarity=0,
            relevance=0,
            uniqueness=0,
            read_count=0,
        )

    def test_get_or_update_read_count(self):
        # without student
        current_read_count = self.tip_rating.read_count

        TipRating.objects.get_or_update_read_count(self.normal_user, self.tip)

        self.tip_rating.refresh_from_db()
        self.assertEqual(current_read_count + 1, self.tip_rating.read_count)

        # with student
        current_read_count = self.tip_rating1.read_count

        TipRating.objects.get_or_update_read_count(
            self.normal_user, self.tip, self.student
        )

        self.tip_rating1.refresh_from_db()
        self.assertEqual(current_read_count + 1, self.tip_rating1.read_count)

    def test_get_or_update_try_count(self):
        # without student
        current_try_count = self.tip_rating.try_count

        TipRating.objects.get_or_update_try_count(self.normal_user, self.tip)

        self.tip_rating.refresh_from_db()
        self.assertEqual(current_try_count + 1, self.tip_rating.try_count)

        # with student
        current_try_count = self.tip_rating1.read_count

        TipRating.objects.get_or_update_try_count(
            self.normal_user, self.tip, self.student
        )

        self.tip_rating1.refresh_from_db()
        self.assertEqual(current_try_count + 1, self.tip_rating1.try_count)

    def test_get_or_update_retry_later(self):
        # without student
        TipRating.objects.get_or_update_retry_later(
            self.normal_user, self.tip, False
        )

        self.tip_rating.refresh_from_db()
        self.assertFalse(self.tip_rating.retry_later)

        TipRating.objects.get_or_update_retry_later(
            self.normal_user, self.tip, True
        )

        self.tip_rating.refresh_from_db()
        self.assertTrue(self.tip_rating.retry_later)

        # with student
        TipRating.objects.get_or_update_retry_later(
            self.normal_user, self.tip, False, self.student
        )

        self.tip_rating1.refresh_from_db()
        self.assertFalse(self.tip_rating1.retry_later)

        TipRating.objects.get_or_update_retry_later(
            self.normal_user, self.tip, True, self.student
        )

        self.tip_rating1.refresh_from_db()
        self.assertTrue(self.tip_rating1.retry_later)

    def test_get_tips_tried(self):
        tip1 = TipFactory.create()
        tip2 = TipFactory.create()

        TipRatingFactory.create(
            added_by=self.normal_user, tip=tip1, try_count=1
        )

        TipRatingFactory.create(
            added_by=self.normal_user, tip=tip2, try_count=0
        )

        expected_tips_tried = 1
        actual_tips_tried = TipRating.objects.get_tips_tried(self.normal_user)

        self.assertEqual(actual_tips_tried, expected_tips_tried)

    def test_get_read_but_not_rated_tip_ratings(self):
        tip_rating1 = TipRatingFactory.create(
            clarity=0, relevance=0, uniqueness=1, read_count=1
        )
        tip_rating2 = TipRatingFactory.create(
            clarity=0, relevance=0, uniqueness=0, read_count=1
        )

        ids = (
            TipRating.objects.get_read_but_not_rated_tip_ratings()
        ).values_list("id", flat=True)

        self.assertNotIn(self.tip_rating.id, ids)
        self.assertNotIn(tip_rating1.id, ids)
        self.assertIn(tip_rating2.id, ids)
