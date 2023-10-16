from django.utils import timezone

import constants
from main.models import Tip
from tasks import dequeue_student_tips
from tests.base_test import BaseTestCase
from tests.factories import (
    ExampleFactory,
    StudentFactory,
    StudentTipFactory,
    TipFactory,
    TipRatingFactory,
    UserFactory,
    UserStudentMappingFactory,
)


class TestTip(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user1 = UserFactory.create(
            role=constants.Role.EXPERIMENTAL_TEACHER
        )
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
            added_by=cls.user1,
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
            added_by=cls.user1,
        )
        ExampleFactory.create(tip=cls.tip1, description="example1")
        ExampleFactory.create(tip=cls.tip2, description="example2")

        cls.user2 = UserFactory.create(
            role=constants.Role.EDUCATOR_CONTENT_EXPERT
        )
        cls.old_tip = TipFactory.create(added_by=cls.user2)
        cls.old_tip.created_at -= timezone.timedelta(days=10)
        cls.old_tip.save()

        cls.student = StudentFactory.create()
        StudentTipFactory.create(student=cls.student, tip=cls.tip1)
        StudentTipFactory.create(student=cls.student, tip=cls.tip2)
        UserStudentMappingFactory.create(
            user=cls.experimental_user,
            student=cls.student,
            added_by=cls.manager_user,
        )
        cls.tip_rating1 = TipRatingFactory.create(
            added_by=cls.experimental_user,
            tip=cls.tip1,
            read_count=1,
            try_count=2,
            clarity=1,
            relevance=2,
            uniqueness=3,
        )
        cls.tip_rating2 = TipRatingFactory.create(
            added_by=cls.experimental_user,
            tip=cls.tip2,
            read_count=1,
            try_count=2,
            clarity=1,
            relevance=2,
            uniqueness=3,
            retry_later=False,
        )

    def test_search_without_search_text(self):
        tips = Tip.objects.search(None, None, None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_title_without_search_fields(self):
        tips = Tip.objects.search(None, "tip1", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(None, "tip", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_title_with_search_fields(self):
        tips = Tip.objects.search(None, "tip1", ["title"])

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(None, "tip", ["title"])

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_description_without_search_fields(self):
        tips = Tip.objects.search(None, "description1", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(None, "description", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_description_with_search_fields(self):
        tips = Tip.objects.search(
            None, "description1", ["title", "description"]
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(
            None, "description", ["title", "description"]
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_sub_goal_without_search_fields(self):
        tips = Tip.objects.search(None, "sub_goal1", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(None, "sub_goal", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_sub_goal_with_search_fields(self):
        tips = Tip.objects.search(
            None, "sub_goal1", ["title", "description", "sub_goal"]
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(
            None, "sub_goal", ["title", "description", "sub_goal"]
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_environment_context_without_search_fields(self):
        tips = Tip.objects.search(None, "SPACE_OPPORTUNITIES_TEST1", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(None, "SPACE_OPPORTUNITIES_TEST", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_environment_context_with_search_fields(self):
        tips = Tip.objects.search(
            None,
            "SPACE_OPPORTUNITIES_TEST1",
            ["title", "environment_context", "child_context"],
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(
            None,
            "SPACE_OPPORTUNITIES_TEST",
            ["title", "environment_context", "child_context"],
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_child_context_without_search_fields(self):
        tips = Tip.objects.search(None, "CURRENT_MOTIVATOR_TEST1", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(None, "CURRENT_MOTIVATOR_TEST", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_child_context_with_search_fields(self):
        tips = Tip.objects.search(
            None,
            "CURRENT_MOTIVATOR_TEST1",
            ["title", "environment_context", "child_context"],
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(
            None,
            "CURRENT_MOTIVATOR_TEST",
            ["title", "environment_context", "child_context"],
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_example_description_without_search_fields(self):
        tips = Tip.objects.search(None, "example1", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(None, "example", None)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_search_example_description_with_search_fields(self):
        tips = Tip.objects.search(
            None, "example1", ["title", "example_description"]
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)

        tips = Tip.objects.search(
            None, "example", ["title", "example_description"]
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)

    def test_contributions_all_users(self):
        data = Tip.objects.contributions()

        self.assertEqual(2, len(data))
        self.assertEqual(2, data[0]["count"])
        self.assertEqual(1, data[1]["count"])

        # create new tip
        new_tip = TipFactory.create()

        data = Tip.objects.contributions()

        new_tip_data = None
        for item in data:
            if item["added_by"] == new_tip.added_by_id:
                new_tip_data = item
                break
        self.assertEqual(1, new_tip_data["count"])

    def test_contributions_one_user(self):
        data = Tip.objects.contributions(user_id=self.user1.id)

        self.assertEqual(1, len(data))
        self.assertEqual(2, data[0]["count"])

    def test_recent_with_user_id(self):
        tips = Tip.objects.by_user_id(user_id=self.old_tip.added_by_id)

        tip_ids = [tip.id for tip in tips]
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)
        self.assertIn(self.old_tip.id, tip_ids)

    def test_filter_by_params_all_users(self):
        tips = Tip.objects.filter_by_params()

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)
        self.assertIn(self.old_tip.id, tip_ids)

    def test_filter_by_params_all_users_with_filter_start_date(self):
        start_date = timezone.localdate() - timezone.timedelta(days=1)
        tips = Tip.objects.filter_by_params(start_date=start_date)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)
        self.assertNotIn(self.old_tip.id, tip_ids)

    def test_filter_by_params_all_users_with_filter_end_date(self):
        end_date = timezone.localdate() - timezone.timedelta(days=5)
        tips = Tip.objects.filter_by_params(end_date=end_date)

        tip_ids = [tip.id for tip in tips]
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)
        self.assertIn(self.old_tip.id, tip_ids)

    def test_filter_by_params_all_users_with_filter_all_date(self):
        start_date = timezone.localdate() - timezone.timedelta(days=18)
        end_date = timezone.localdate() - timezone.timedelta(days=9)
        tips = Tip.objects.filter_by_params(
            start_date=start_date, end_date=end_date
        )

        tip_ids = [tip.id for tip in tips]
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)
        self.assertIn(self.old_tip.id, tip_ids)

    def test_filter_by_params_all_users_with_filter_role_and_start_date(self):
        start_date = timezone.localdate() - timezone.timedelta(days=5)
        tips = Tip.objects.filter_by_params(
            start_date=start_date, role=constants.Role.EXPERIMENTAL_TEACHER
        )

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertIn(self.tip2.id, tip_ids)
        self.assertNotIn(self.old_tip.id, tip_ids)

    def test_filter_by_params_all_users_with_filter_role_and_end_date(self):
        end_date = timezone.localdate() - timezone.timedelta(days=30)
        tips = Tip.objects.filter_by_params(
            end_date=end_date, role=constants.Role.EDUCATOR_SHADOW
        )

        tip_ids = [tip.id for tip in tips]
        self.assertNotIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)
        self.assertNotIn(self.old_tip.id, tip_ids)

    def test_by_dlp(self):
        dequeue_student_tips(9999)

        tips = Tip.objects.by_dlp(self.experimental_user)

        tip_ids = [tip.id for tip in tips]
        self.assertIn(self.tip1.id, tip_ids)
        self.assertNotIn(self.tip2.id, tip_ids)
