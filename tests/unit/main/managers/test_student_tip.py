import constants
from main.models import StudentTip
from tests.base_test import BaseTestCase
from tests.factories import (
    ExampleFactory,
    StudentFactory,
    StudentTipFactory,
    TipFactory,
    TipRatingFactory,
)


class TestStudentTip(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.tip1 = TipFactory.create(
            title="tip1",
            description="description1",
            environment_context={
                constants.Environment.SPACE_OPPORTUNITIES: "SPACE_OPPORTUNITIES_TEST1",
                constants.Environment.SPACE_EXPECTATIONS: "new1",
            },
            child_context={
                constants.ChildContext.CURRENT_MOTIVATOR: "CURRENT_MOTIVATOR_TEST1",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "old1",
            },
            sub_goal="sub_goal1",
        )

        cls.tip2 = TipFactory.create(
            title="tip2",
            description="description2",
            environment_context={
                constants.Environment.SPACE_OPPORTUNITIES: "SPACE_OPPORTUNITIES_TEST2",
                constants.Environment.SPACE_EXPECTATIONS: "new2",
            },
            child_context={
                constants.ChildContext.CURRENT_MOTIVATOR: "CURRENT_MOTIVATOR_TEST2",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "old2",
            },
            sub_goal="sub_goal2",
        )
        ExampleFactory.create(tip=cls.tip1, description="example1")
        ExampleFactory.create(tip=cls.tip2, description="example2")

        cls.student1 = StudentFactory.create()
        cls.student2 = StudentFactory.create()

        cls.student_tip1 = StudentTipFactory.create(
            student=cls.student1, tip=cls.tip1
        )
        cls.student_tip2 = StudentTipFactory.create(
            student=cls.student2, tip=cls.tip2
        )

    def test_search_without_search_text(self):
        student_tips = StudentTip.objects.search(None, None, None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_title_without_search_fields(self):
        student_tips = StudentTip.objects.search(None, "tip1", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(None, "tip", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_title_with_search_fields(self):
        student_tips = StudentTip.objects.search(None, "tip1", ["title"])

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(None, "tip", ["title"])

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_description_without_search_fields(self):
        student_tips = StudentTip.objects.search(None, "description1", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(None, "description", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_description_with_search_fields(self):
        student_tips = StudentTip.objects.search(
            None, "description1", ["title", "description"]
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(
            None, "description", ["title", "description"]
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_sub_goal_without_search_fields(self):
        student_tips = StudentTip.objects.search(None, "sub_goal1", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(None, "sub_goal", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_sub_goal_with_search_fields(self):
        student_tips = StudentTip.objects.search(
            None, "sub_goal1", ["title", "description", "sub_goal"]
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(
            None, "sub_goal", ["title", "description", "sub_goal"]
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_environment_context_without_search_fields(self):
        student_tips = StudentTip.objects.search(
            None, "SPACE_OPPORTUNITIES_TEST1", None
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(
            None, "SPACE_OPPORTUNITIES_TEST", None
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_environment_context_with_search_fields(self):
        student_tips = StudentTip.objects.search(
            None,
            "SPACE_OPPORTUNITIES_TEST1",
            ["title", "environment_context", "child_context"],
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(
            None,
            "SPACE_OPPORTUNITIES_TEST",
            ["title", "environment_context", "child_context"],
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_child_context_without_search_fields(self):
        student_tips = StudentTip.objects.search(
            None, "CURRENT_MOTIVATOR_TEST1", None
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(
            None, "CURRENT_MOTIVATOR_TEST", None
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_child_context_with_search_fields(self):
        student_tips = StudentTip.objects.search(
            None,
            "CURRENT_MOTIVATOR_TEST1",
            ["title", "environment_context", "child_context"],
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(
            None,
            "CURRENT_MOTIVATOR_TEST",
            ["title", "environment_context", "child_context"],
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_example_description_without_search_fields(self):
        student_tips = StudentTip.objects.search(None, "example1", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(None, "example", None)

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_search_example_description_with_search_fields(self):
        student_tips = StudentTip.objects.search(
            None, "example1", ["title", "example_description"]
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertNotIn(self.student_tip2.id, student_tip_ids)

        student_tips = StudentTip.objects.search(
            None, "example", ["title", "example_description"]
        )

        student_tip_ids = [student_tip.id for student_tip in student_tips]
        self.assertIn(self.student_tip1.id, student_tip_ids)
        self.assertIn(self.student_tip2.id, student_tip_ids)

    def test_annotate_browse_tips_is_read_false(self):
        user = self.student_tip2.added_by

        student_tip = StudentTip.objects.annotate_browse_tips(
            user, self.student_tip1.student_id
        ).first()

        self.assertFalse(student_tip.is_read)

    def test_annotate_browse_tips_is_rated_true(self):
        user = self.student_tip1.added_by

        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            added_by_id=user.id,
            student_id=self.student_tip1.student_id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        student_tip = StudentTip.objects.annotate_browse_tips(
            user, self.student_tip1.student_id
        ).first()

        self.assertTrue(student_tip.is_rated)

    def test_annotate_browse_tips_is_rated_false(self):
        user = self.student_tip1.added_by

        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=0,
            relevance=3,
            uniqueness=5,
        )

        student_tip = StudentTip.objects.annotate_browse_tips(
            user, self.student_tip1.student_id
        ).first()

        self.assertFalse(student_tip.is_rated)

    def test_annotate_browse_tips(self):
        user = self.student_tip1.added_by

        tip_rating = TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            read_count=5,
            try_count=6,
            helpful_count=7,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        student_tip = (
            StudentTip.objects.annotate_browse_tips(
                user, self.student_tip1.student_id
            )
            .filter(id=self.student_tip1.id)
            .first()
        )

        self.assertEqual(student_tip.read_count, tip_rating.read_count)
        self.assertEqual(student_tip.try_count, tip_rating.try_count)
        self.assertEqual(student_tip.helpful_count, tip_rating.helpful_count)
        self.assertEqual(student_tip.read_count, tip_rating.read_count)
        self.assertTrue(student_tip.is_read)
        self.assertTrue(student_tip.is_rated)

    def test_annotate_browse_tips_with_student_is_none_and_check_is_rated_is_false(
        self,
    ):
        user = self.student_tip1.added_by

        # false
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=None,
            added_by_id=user.id,
            retry_later=True,
            clarity=0,
            relevance=3,
            uniqueness=5,
        )

        student_tip = StudentTip.objects.annotate_browse_tips(
            user, self.student_tip1.student_id
        ).first()

        self.assertFalse(student_tip.is_rated)

    def test_annotate_browse_tips_with_student_is_none_and_check_is_rated_is_true(
        self,
    ):
        user = self.student_tip1.added_by

        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        student_tip = StudentTip.objects.annotate_browse_tips(
            user, self.student_tip1.student_id
        ).first()

        self.assertTrue(student_tip.is_rated)

    def test_annotate_browse_tips_with_student_is_not_none_and_check_is_rated_is_false(
        self,
    ):
        user = self.student_tip1.added_by

        # false
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=0,
            relevance=3,
            uniqueness=5,
        )

        student_tip = (
            StudentTip.objects.annotate_browse_tips(
                user, self.student_tip1.student_id
            )
            .filter(id=self.student_tip1.id)
            .first()
        )

        self.assertFalse(student_tip.is_rated)

    def test_annotate_browse_tips_with_student_is_not_none_and_check_is_rated_is_true(
        self,
    ):
        user = self.student_tip1.added_by

        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        student_tip = (
            StudentTip.objects.annotate_browse_tips(
                user, self.student_tip1.student_id
            )
            .filter(id=self.student_tip1.id)
            .first()
        )

        self.assertTrue(student_tip.is_rated)

    def test_annotate_browse_tips_with_check_is_rated_is_false(self):
        user = self.student_tip1.added_by

        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=0,
            relevance=3,
            uniqueness=5,
        )

        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=None,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=0,
            uniqueness=5,
        )

        student_tip = (
            StudentTip.objects.annotate_browse_tips(
                user, self.student_tip1.student_id
            )
            .filter(id=self.student_tip1.id)
            .first()
        )

        self.assertFalse(student_tip.is_rated)

    def test_annotate_browse_tips_with_check_is_rated_is_true_scenario_1(self):
        user = self.student_tip1.added_by

        # tip rating is rated with student is not none
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        # tip rating is rated with student is none
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=None,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        student_tip = (
            StudentTip.objects.annotate_browse_tips(
                user, self.student_tip1.student_id
            )
            .filter(id=self.student_tip1.id)
            .first()
        )

        self.assertTrue(student_tip.is_rated)

    def test_annotate_browse_tips_with_check_is_rated_is_true_scenario_2(self):
        user = self.student_tip1.added_by

        # tip rating is not rated with student is not none
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        # tip rating is rated with student is none
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=None,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        student_tip = (
            StudentTip.objects.annotate_browse_tips(
                user, self.student_tip1.student_id
            )
            .filter(id=self.student_tip1.id)
            .first()
        )

        self.assertTrue(student_tip.is_rated)

    def test_annotate_browse_tips_with_check_is_rated_is_true_scenario_3(self):
        user = self.student_tip1.added_by

        # tip rating is rated with student is not none
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=self.student_tip1.student_id,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=3,
            uniqueness=5,
        )

        # tip rating is not rated with student is none
        TipRatingFactory.create(
            tip_id=self.student_tip1.tip_id,
            student_id=None,
            added_by_id=user.id,
            retry_later=True,
            clarity=1,
            relevance=0,
            uniqueness=5,
        )

        student_tip = (
            StudentTip.objects.annotate_browse_tips(
                user, self.student_tip1.student_id
            )
            .filter(id=self.student_tip1.id)
            .first()
        )

        self.assertTrue(student_tip.is_rated)
