from django.urls import reverse
from django.utils import timezone
from notifications.models import Notification
from rest_framework import status
from reversion.models import Version

import constants
from main.models import StudentTip, Tip, TipRating
from tasks import dequeue_student_tips
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    StudentFactory,
    StudentTipFactory,
    TagFactory,
    TaggedTipFactory,
    TipFactory,
    TipRatingFactory,
    UserStudentMappingFactory,
)


class TestTipAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:tips-list")

        cls.tip1 = TipFactory.create(
            title="tip 1", description="description 1", marked_for_editing=True
        )
        cls.tip2 = TipFactory.create(
            title="tip 2", description="description 2"
        )

        cls.tip3 = TipFactory.create(
            title="tip 3",
            description="description 3",
        )
        cls.tip4 = TipFactory.create(
            title="new tip 4",
            description="description 4",
        )
        cls.student = StudentFactory.create()
        StudentTipFactory.create(
            student=cls.student,
            tip=cls.tip1,
            is_graduated=True,
            is_queued=False,
        )
        StudentTipFactory.create(
            student=cls.student,
            tip=cls.tip2,
            is_graduated=True,
            is_queued=False,
        )
        StudentTipFactory.create(
            student=cls.student,
            tip=cls.tip3,
            is_graduated=True,
            is_queued=True,
        )
        StudentTipFactory.create(
            student=cls.student,
            tip=cls.tip4,
            is_queued=True,
        )
        UserStudentMappingFactory.create(
            user=cls.experimental_user,
            student=cls.student,
            added_by=cls.manager_user,
        )

        cls.tip_rating1 = TipRatingFactory.create(
            added_by=cls.experimental_user,
            tip=cls.tip3,
            read_count=1,
            try_count=2,
            clarity=3,
            relevance=4,
            uniqueness=5,
        )
        cls.tip_rating2 = TipRatingFactory.create(
            added_by=cls.experimental_user,
            tip=cls.tip4,
            read_count=2,
            try_count=3,
            clarity=4,
            relevance=5,
            uniqueness=6,
            retry_later=False,
        )

        cls.tip_rating3 = TipRatingFactory.create(
            added_by=cls.guest_user,
            tip=cls.tip3,
            read_count=3,
            try_count=4,
            clarity=5,
            relevance=6,
            uniqueness=7,
        )

        cls.tip5 = TipFactory.create(
            title="new tip 5",
            description="description 5",
        )
        cls.student1 = StudentFactory.create()
        StudentTipFactory.create(
            student=cls.student1,
            tip=cls.tip5,
            is_graduated=True,
        )
        UserStudentMappingFactory.create(
            user=cls.experimental_user,
            student=cls.student1,
            added_by=cls.manager_user,
        )

        cls.detail_url = reverse("v1:tips-detail", args=[cls.tip1.id])
        cls.suggest_url = reverse("v1:tips-suggest", args=[cls.tip1.id])
        cls.versions_url = reverse("v1:tips-versions", args=[cls.tip1.id])
        cls.recover_url = reverse("v1:tips-recover", args=[cls.tip1.id])
        cls.try_url = reverse("v1:tips-try-tip", args=[cls.tip3.id])

        cls.expected_detail_keys = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "description",
            "group_context",
            "helpful",
            "howto",
            "when",
            "persuasive",
            "sub_goal",
            "related_tips",
            "overarching_goal",
            "child_context",
            "child_context_flattened",
            "environment_context",
            "environment_context_flattened",
            "updated_by",
            "linked_tips",
            "marked_for_editing",
            "average_rating",
            "clarity_average_rating",
            "relevance_average_rating",
            "uniqueness_average_rating",
            "created_at",
            "created_by",
            "updated_at",
            "updated",
            "added_by",
            "read_count",
            "try_count",
            "is_rated",
            "helpful_count",
            "tags",
            "tip_summary",
        ]
        cls.expected_list_keys = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "read_count",
            "try_count",
            "is_rated",
            "helpful_count",
            "tip_summary",
        ]
        cls.expected_detail_keys_for_dlp_user = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "description",
            "group_context",
            "helpful",
            "helpful_count",
            "howto",
            "when",
            "persuasive",
            "sub_goal",
            "related_tips",
            "overarching_goal",
            "updated_by",
            "child_context",
            "child_context_flattened",
            "environment_context",
            "environment_context_flattened",
            "linked_tips",
            "marked_for_editing",
            "average_rating",
            "clarity_average_rating",
            "relevance_average_rating",
            "uniqueness_average_rating",
            "created_at",
            "updated_at",
            "updated",
            "added_by",
            "is_rated",
            "read_count",
            "try_count",
            "graduated_for",
            "tags",
            "created_by",
            "tip_summary",
        ]

        cls.maxDiff = None

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(
            self.list_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        tip = response.data["results"][0]
        self.assertEqual(sorted(self.expected_list_keys), sorted(tip.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)

    def test_get_list_success_with_filter_tag(self):
        # prepare data
        tag1 = TagFactory.create(name="name_1", slug="slug_1")
        tag2 = TagFactory.create(name="name_2", slug="slug_2")
        TaggedTipFactory.create(content_object=self.tip1, tag=tag1)
        TaggedTipFactory.create(content_object=self.tip2, tag=tag1)
        TaggedTipFactory.create(content_object=self.tip3, tag=tag1)
        TaggedTipFactory.create(content_object=self.tip4, tag=tag2)
        TaggedTipFactory.create(content_object=self.tip5, tag=tag2)

        # tag = tag1.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": tag1.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertNotIn(self.tip4.id, ids)
        self.assertNotIn(self.tip5.id, ids)

        # tag = tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": tag2.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertNotIn(self.tip3.id, ids)
        self.assertIn(self.tip4.id, ids)
        self.assertIn(self.tip5.id, ids)

        # tag = tag1.name, tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": "{},{}".format(tag1.name, tag2.name)},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertIn(self.tip4.id, ids)
        self.assertIn(self.tip5.id, ids)

    def test_get_list_success_with_role_dlp(self):
        dequeue_student_tips(9999)
        tip_x = TipFactory.create()
        StudentTipFactory.create(
            student=self.student,
            tip=tip_x,
            is_graduated=True,
            is_queued=True,
        )

        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"ordering": "id"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertNotIn(self.tip4.id, ids)
        self.assertNotIn(tip_x.id, ids)

        results = response.data["results"]
        data = results[0]
        for item in results:
            if item["id"] == self.tip3.id:
                data = item
                break

        expected_list_keys_for_dlp_user = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "helpful_count",
            "read_count",
            "try_count",
            "is_rated",
            "graduated_for",
            "tip_summary",
        ]
        self.assertEqual(
            sorted(expected_list_keys_for_dlp_user), sorted(data.keys())
        )
        self.assertEqual(1, data["read_count"])
        self.assertEqual(2, data["try_count"])
        self.assertTrue(data["is_rated"])
        self.assertTrue(data["graduated_for"])

    def test_get_list_with_dlp_filter_student_id(self):
        dequeue_student_tips(9999)
        tip_x = TipFactory.create()
        StudentTipFactory.create(
            student=self.student,
            tip=tip_x,
            is_graduated=True,
            is_queued=True,
        )

        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"student": self.student.id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertNotIn(self.tip4.id, ids)
        self.assertNotIn(tip_x.id, ids)

    def test_get_list_with_filter_student_id(self):
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"student": self.student.id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertIn(self.tip4.id, ids)

    def test_get_list_with_dlp_filter_graduated_for(self):
        dequeue_student_tips(9999)
        tip_x = TipFactory.create()
        StudentTipFactory.create(
            student=self.student,
            tip=tip_x,
            is_graduated=True,
            is_queued=True,
        )

        response = self.authenticated_dlp_client.get(
            self.list_url,
            {"graduated_for": self.student.id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertNotIn(self.tip4.id, ids)
        self.assertNotIn(tip_x.id, ids)

    def test_get_list_with_filter_graduated_for(self):
        response = self.authenticated_manager_client.get(
            self.list_url,
            {
                "graduated_for": "{},{}".format(
                    self.student.id, self.student1.id
                )
            },
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertNotIn(self.tip4.id, ids)
        self.assertIn(self.tip5.id, ids)

    def test_get_list_with_manager_filter_user(self):
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"user": self.experimental_user.id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertIn(self.tip4.id, ids)
        self.assertIn(self.tip5.id, ids)

    def test_get_list_with_manager_filter_student_and_is_queued(self):
        # user = self.experimental, is_queued = False
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"student": self.student.id, "is_queued": False},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)
        self.assertNotIn(self.tip3.id, ids)
        self.assertNotIn(self.tip4.id, ids)
        self.assertNotIn(self.tip5.id, ids)

        # user = self.experimental, is_queued = True
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"student": self.student.id, "is_queued": True},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertIn(self.tip3.id, ids)
        self.assertIn(self.tip4.id, ids)
        self.assertNotIn(self.tip5.id, ids)

    def test_get_list_with_filter_graduated_for_check_duplicate(self):
        student = StudentFactory.create()
        StudentTipFactory.create(
            student=student, tip=self.tip3, is_graduated=True
        )

        response = self.authenticated_manager_client.get(
            self.list_url,
            {"graduated_for": "{}".format(student.id)},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual([self.tip3.id], ids)

    def test_get_list_with_filter_page_not_found(self):
        response = self.forced_authenticated_client.get(
            self.list_url, {"page": 99999999}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected = [
            ("count", None),
            ("next", None),
            ("previous", None),
            ("results", []),
        ]
        for item in expected:
            self.assertEqual(response.data[item[0]], item[1])

    def test_get_list_with_filter_linked_tip(self):
        self.tip1.linked_tips.add(self.tip2)
        # linked_tip = tip 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"linked_tip": self.tip1.id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)

        # linked_tip = tip 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"linked_tip": self.tip2.id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)

    def test_get_list_with_filter_title(self):
        # title = tip 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"title": self.tip1.title}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)

        # title tip 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"title": self.tip2.title}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)

    def test_get_list_with_filter_marked_for_editing(self):
        # marked_for_editing = tip 1
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"marked_for_editing": self.tip1.marked_for_editing},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)

        # marked_for_editing tip 2
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"marked_for_editing": self.tip2.marked_for_editing},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)

    def test_get_list_with_filter_description(self):
        # description = tip 1
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"description": self.tip1.description},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)

        # description tip X
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"description": self.tip2.description},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)

    def test_get_list_with_filter_updated_by(self):
        # updated_by_id is from tip 1
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"updated_by": self.tip1.updated_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)

        # updated_by_id is from tip 2
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"updated_by": self.tip2.updated_by_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertIn(self.tip2.id, ids)

    def test_search_text(self):
        self.tip1.sub_goal = "SUB_GOAL_TEST"
        self.tip1.save()

        # search_text is sub_goal of tip 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"search_text": self.tip1.sub_goal}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)

        # search_text is new environment_context
        data = {
            "state": constants.States.PAUSING,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "1111 breathing 33-flower 22",
            "description": "2222 See 22 Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "ENVIRONMENT_CONTEXT_TEST",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
            },
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )
        new_tip_ip1 = response.data["id"]

        response = self.forced_authenticated_client.get(
            self.list_url,
            {"search_text": "ENVIRONMENT_CONTEXT_TEST"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertIn(new_tip_ip1, ids)

        # search_text is new child_context
        data = {
            "state": constants.States.PAUSING,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "1111 11 techniques-flower ok",
            "description": "2222 ddd Outside Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "SEARCH_TEXT_TEST",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "CHILD_CONTEXT_TEST",
            },
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )
        new_tip_ip2 = response.data["id"]

        response = self.forced_authenticated_client.get(
            self.list_url, {"search_text": "CHILD_CONTEXT_TEST"}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertNotIn(new_tip_ip1, ids)
        self.assertIn(new_tip_ip2, ids)

    def test_search_text_and_search_fields(self):
        self.tip1.sub_goal = "SUB_GOAL_TEST"
        self.tip1.save()

        # search_text is sub_goal of tip 1 - with search_fields as sub_goal
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"search_text": self.tip1.sub_goal, "search_fields": "sub_goal"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)

        # search_text is sub_goal of tip 1 - with search_fields as description
        response = self.forced_authenticated_client.get(
            self.list_url,
            {
                "search_text": self.tip1.sub_goal,
                "search_fields": "description",
            },
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data["results"]))

        # search_text is new environment_context
        data = {
            "state": constants.States.PAUSING,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "1111 breathing 33-flower 22",
            "description": "2222 See 22 Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "ENVIRONMENT_CONTEXT_TEST",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
            },
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )
        new_tip_ip1 = response.data["id"]

        response = self.forced_authenticated_client.get(
            self.list_url,
            {"search_text": "ENVIRONMENT_CONTEXT_TEST"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertIn(new_tip_ip1, ids)

        # search_text is new environment_context - search_fields is not environment_context
        response = self.forced_authenticated_client.get(
            self.list_url,
            {
                "search_text": "ENVIRONMENT_CONTEXT_TEST",
                "search_fields": "description,title",
            },
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data["results"]))

        # search_text is new child_context
        data = {
            "state": constants.States.PAUSING,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "1111 11 techniques-flower ok",
            "description": "2222 ddd Outside Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "SEARCH_TEXT_TEST",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "CHILD_CONTEXT_TEST",
            },
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )
        new_tip_ip2 = response.data["id"]

        response = self.forced_authenticated_client.get(
            self.list_url, {"search_text": "CHILD_CONTEXT_TEST"}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.tip1.id, ids)
        self.assertNotIn(self.tip2.id, ids)
        self.assertNotIn(new_tip_ip1, ids)
        self.assertIn(new_tip_ip2, ids)

        # search_text is new child_context - search_fields is not child_context
        response = self.forced_authenticated_client.get(
            self.list_url,
            {
                "search_text": "ENVIRONMENT_CONTEXT_TEST",
                "search_fields": "description,title,sub_goal",
            },
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data["results"]))

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tip1.id, response.data["id"])

    def test_get_detail_success_with_dlp_user_check_is_rated(self):
        dequeue_student_tips(9999)
        detail_url = reverse("v1:tips-detail", args=[self.tip3.id])

        response = self.authenticated_dlp_client.get(detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.expected_detail_keys_for_dlp_user),
            sorted(response.data.keys()),
        )

        self.assertEqual(self.tip3.id, response.data["id"])
        self.assertTrue(response.data["is_rated"])

    def test_get_detail_success_with_dlp_user_check_graduated_for(self):
        dequeue_student_tips(9999)

        detail_url = reverse("v1:tips-detail", args=[self.tip3.id])

        response = self.authenticated_dlp_client.get(detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.expected_detail_keys_for_dlp_user),
            sorted(response.data.keys()),
        )

        self.assertEqual(self.tip3.id, response.data["id"])
        self.assertTrue(response.data["graduated_for"])

    def test_get_detail_success_with_ratings(self):
        rating1 = TipRatingFactory.create(
            tip=self.tip1, added_by=self.normal_user
        )

        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.tip1.id, response.data["id"])
        self.assertEqual(
            rating1.clarity, response.data["clarity_average_rating"]
        )
        self.assertEqual(
            rating1.relevance, response.data["relevance_average_rating"]
        )
        self.assertEqual(
            rating1.uniqueness, response.data["uniqueness_average_rating"]
        )
        tip = self.tip1
        tip.refresh_from_db()
        self.assertEqual(tip.average_rating, response.data["average_rating"])

    def test_get_detail_success_check_tags(self):
        # add tag
        tag = TagFactory.create(name="name_1")
        TaggedTipFactory.create(content_object=self.tip1, tag=tag)

        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertListEqual(["name_1"], response.data["tags"])

    def test_get_detail_success_with_check_read_tip_notification(self):
        detail_url = reverse("v1:tips-detail", args=[self.tip3.id])
        response = self.forced_authenticated_client.get(detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        # check create notification
        is_existed = Notification.objects.filter(
            actor_object_id=self.normal_user.id,
            recipient_id=self.normal_user.id,
            verb=constants.Activity.READ_TIP,
            description="{} read the tip {}".format(
                self.tip_rating1.added_by.full_name,
                self.tip_rating1.tip.title,
            ),
        ).exists()
        self.assertTrue(is_existed)

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:tips-detail", args=[-1])
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_success(self):
        data = {
            "state": constants.States.PAUSING,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "breathing techniques-flower 22",
            "description": "See Outside Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "test",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
            },
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.tip1.refresh_from_db()
        self.assertEqual(data["tip_summary"], self.tip1.tip_summary)

        self.assertEqual(self.tip1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertEqual(
            self.normal_user.id, response.data["updated_by"]["id"]
        )
        self.assertEqual(
            self.normal_user.full_name,
            response.data["updated_by"]["full_name"],
        )

    def test_update_with_full_detail_fail(self):
        data = {
            "state": 1111,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "breathing techniques-flower 22",
            "description": "See Outside Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "test",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
            },
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("state", response.data)

    def test_update_with_partial_detail(self):
        data = {
            "title": "new title",
            "description": "new description",
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.tip1.refresh_from_db()
        self.assertEqual(data["tip_summary"], self.tip1.tip_summary)

        self.assertEqual(self.tip1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])
        self.assertEqual(
            self.normal_user.id, response.data["updated_by"]["id"]
        )
        self.assertEqual(
            self.normal_user.full_name,
            response.data["updated_by"]["full_name"],
        )

    def test_update_with_partial_detail_fail(self):
        data = {"substate": "INVALID substate"}

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("substate", response.data)

    def test_delete_success(self):
        tip4 = TipFactory.create(title="tip 4")

        response = self.forced_authenticated_client.delete(
            reverse("v1:tips-detail", args=[tip4.id])
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.forced_authenticated_client.get(
            reverse("v1:tips-detail", args=[tip4.id])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:tips-detail", args=[-1])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_success(self):
        data = {
            "state": constants.States.PAUSING,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "1111 breathing techniques-flower 22",
            "description": "2222 See Outside Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "test",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
            },
            "linked_tips": [self.tip1.id],
            "marked_for_editing": True,
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            sorted(self.expected_detail_keys),
            sorted(response.data.keys()),
        )

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertEqual(
            self.normal_user.id, response.data["updated_by"]["id"]
        )
        self.assertEqual(
            self.normal_user.full_name,
            response.data["updated_by"]["full_name"],
        )

    def test_create_fail(self):
        data = {
            "state": constants.States.PAUSING,
            "substate": 112123,
            "levels": constants.Levels.LEVEL_1,
            "title": "breathing techniques-flower 22",
            "description": "See Outside Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "test",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
            },
            "marked_for_editing": True,
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("substate", response.data)

    def test_suggest_success(self):
        new_student1 = StudentFactory.create()
        new_student2 = StudentFactory.create()
        old_count = StudentTip.objects.count()

        data = {"students": [new_student1.id, new_student2.id]}

        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        new_count = StudentTip.objects.count()
        self.assertEqual(old_count + 2, new_count)

        data = {"students": [new_student1.id, new_student2.id]}

        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        new_count1 = StudentTip.objects.count()
        self.assertEqual(new_count1, new_count)

    def test_suggest_success_with_existing_student_tip(self):
        new_student1 = StudentFactory.create()

        new_student2 = StudentFactory.create()
        StudentTipFactory.create(
            tip=self.tip1,
            student=new_student2,
        )

        old_count = StudentTip.objects.count()

        data = {
            "students": [new_student1.id, new_student2.id],
        }

        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        new_count = StudentTip.objects.count()
        self.assertEqual(old_count + 1, new_count)

        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        new_count1 = StudentTip.objects.count()
        self.assertEqual(new_count1, new_count)

    def test_suggest_success_with_check_last_suggested_at(self):
        new_student1 = StudentFactory.create()

        new_student2 = StudentFactory.create()
        student2_tip1 = StudentTipFactory.create(
            tip=self.tip1,
            student=new_student2,
        )

        count1 = StudentTip.objects.count()

        data = {
            "students": [new_student1.id, new_student2.id],
        }

        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        count2 = StudentTip.objects.count()
        self.assertEqual(count1 + 1, count2)

        # check last_suggested_at is updated
        student1_tip1 = StudentTip.objects.get(
            tip=self.tip1,
            student=new_student1,
        )
        last_suggested_at1 = student1_tip1.last_suggested_at

        student2_tip1.refresh_from_db()
        last_suggested_at2 = student2_tip1.last_suggested_at

        self.assertIsNotNone(last_suggested_at1)
        self.assertIsNotNone(last_suggested_at2)

        # check re-suggest
        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        count3 = StudentTip.objects.count()
        self.assertEqual(count2, count3)

        # check last_suggested_at is updated
        student1_tip1.refresh_from_db()
        student2_tip1.refresh_from_db()

        new_last_suggested_at1 = student1_tip1.last_suggested_at
        new_last_suggested_at2 = student2_tip1.last_suggested_at

        self.assertLess(last_suggested_at1, new_last_suggested_at1)
        self.assertLess(last_suggested_at2, new_last_suggested_at2)

    # https://app.asana.com/0/1200522294205852/1201975456384516/f
    def test_suggest_success_with_specific_scenario(self):
        # prepare data
        tip = TipFactory.create()
        tip.created_at = timezone.now() - timezone.timedelta(days=365 * 2)
        tip.save()

        student = StudentFactory.create()

        student_tip = StudentTipFactory.create(tip=tip, student=student)
        student_tip.last_suggested_at = timezone.now() - timezone.timedelta(
            days=30 * 6
        )
        student_tip.save()

        suggest_url = reverse("v1:tips-suggest", args=[tip.id])

        # re-suggest
        data = {
            "students": [student.id],
        }

        response = self.forced_authenticated_client.post(
            suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        student_tip.refresh_from_db()
        self.assertLess(
            timezone.now() - timezone.timedelta(days=30 * 6),
            student_tip.last_suggested_at,
        )

        # test student_tip main with filter last_suggested_at
        data = {
            "start_date": timezone.now() - timezone.timedelta(days=7 * 3),
            "end_date": timezone.now(),
        }

        student_tip_url = reverse("v1:student-tips-list", args=[student.id])
        response = self.forced_authenticated_client.get(
            student_tip_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(student_tip.id, ids)

    def test_suggest_success_with_check_suggest_tip_notification(self):
        student = StudentFactory.create()
        old_count = StudentTip.objects.count()

        data = {"students": [student.id]}

        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({"status": "created"}, response.data)

        new_count = StudentTip.objects.count()
        self.assertEqual(old_count + 1, new_count)

        # check create notification
        is_existed = Notification.objects.filter(
            actor_object_id=self.normal_user.id,
            recipient_id=self.normal_user.id,
            verb=constants.Activity.SUGGEST_TIP,
            description="{} assigned the tip {} for the student {}".format(
                self.normal_user.full_name,
                self.tip1.title,
                student.full_name,
            ),
        ).exists()
        self.assertTrue(is_existed)

    def test_suggest_fail(self):
        data = {"students": [90000, 90001]}

        response = self.forced_authenticated_client.post(
            self.suggest_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("students", response.data)

    def test_create_new_version_when_create_success(self):
        data = {
            "state": constants.States.PAUSING,
            "substate": constants.SubStates.ACCOMMODATE,
            "levels": constants.Levels.LEVEL_1,
            "title": "1111 breathing techniques-flower 22",
            "description": "2222 See Outside Programs, 11 techniques",
            "group_context": "group_context-xxssyy",
            "helpful": "helpful-xxssyy",
            "howto": "howto-xxssyy",
            "when": "when-xxssyy",
            "persuasive": "persuasive-xxssyy",
            "sub_goal": "sub_goal-xxssyy",
            "related_tips": "related_tips-xxssyy",
            "overarching_goal": "overarching_goal-xxssyy",
            "environment_context": {
                constants.Environment.SPACE_OPPORTUNITIES: "test",
                constants.Environment.SPACE_EXPECTATIONS: "new",
            },
            "child_context": {
                constants.ChildContext.CURRENT_MOTIVATOR: "test",
                constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
            },
            "linked_tips": [self.tip1.id],
            "marked_for_editing": True,
            "tip_summary": "this is a new tip summary",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )
        tip_id = response.data["id"]
        tip = Tip.objects.get(pk=tip_id)
        version = Version.objects.get_for_object(tip).first()
        tip_field_dict = version.field_dict
        reversion = version.revision

        for key in data.keys():
            self.assertEqual(tip_field_dict[key], response.data[key])

        self.assertEqual("", reversion.comment)
        self.assertEqual(self.normal_user.id, reversion.user_id)

    def test_create_new_version_when_update_success(self):
        data = {"title": "new title"}
        versions = Version.objects.get_for_object(self.tip1)
        old_verions_count = versions.count()

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        tip_id = response.data["id"]
        tip = Tip.objects.get(pk=tip_id)
        new_verions_count = versions.count()
        self.assertEqual(old_verions_count + 1, new_verions_count)

        version = Version.objects.get_for_object(tip).first()
        tip_field_dict = version.field_dict
        reversion = version.revision

        for key in data.keys():
            self.assertEqual(tip_field_dict[key], data[key])

        self.assertEqual("", reversion.comment)
        self.assertEqual(self.normal_user.id, reversion.user_id)

    def test_get_versions_success_with_manager_user(self):
        data = {"title": "new title"}

        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        versions = Version.objects.get_for_object(self.tip1)
        tip_ids = [version.field_dict.get("id") for version in versions]

        # check with role admin
        response = self.authenticated_admin_client.get(self.versions_url)
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual(tip_ids, expected_value)

        # check with role manager
        response = self.authenticated_manager_client.get(self.versions_url)
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual(tip_ids, expected_value)

    def test_get_versions_with_filter_success_with_manager_user(self):
        data = {"title": "new title"}

        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        version = Version.objects.get_for_object(self.tip1).first()
        tip_id = version.field_dict.get("id")

        filter_data = {"version": version.id}

        # check with role admin
        response = self.authenticated_admin_client.get(
            self.versions_url, data=filter_data
        )
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual([tip_id], expected_value)

        # check with role manager
        response = self.authenticated_manager_client.get(
            self.versions_url, data=filter_data
        )
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual([tip_id], expected_value)

    def test_recover_with_not_params_success_with_admin_user(self):
        data = {"title": "new title"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"title": "new title 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        response = self.authenticated_admin_client.post(self.recover_url)
        self.tip1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new title", self.tip1.title)

    def test_recover_with_params_success_with_admin_user(self):
        data = {"title": "new title"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"title": "new title 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"title": "new title 2"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        version = Version.objects.get_for_object(self.tip1)[2]
        response = self.authenticated_admin_client.post(
            self.recover_url, data={"version": version.id}
        )
        self.tip1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new title", self.tip1.title)

    def test_recover_with_not_params_success_with_manager_user(self):
        data = {"title": "new title"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"title": "new title 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        response = self.authenticated_manager_client.post(self.recover_url)
        self.tip1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new title", self.tip1.title)

    def test_recover_with_params_success_with_manager_user(self):
        data = {"title": "new title"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"title": "new title 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"title": "new title 2"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        version = Version.objects.get_for_object(self.tip1)[2]
        response = self.authenticated_manager_client.post(
            self.recover_url, data={"version": version.id}
        )
        self.tip1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new title", self.tip1.title)

    def test_get_versions_fail_with_normal_user(self):
        response = self.forced_authenticated_client.get(self.versions_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recover_fail_with_normal_user(self):
        response = self.forced_authenticated_client.get(self.versions_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_success_with_check_read_count(self):
        is_existed = TipRating.objects.filter(
            added_by=self.manager_user, tip=self.tip1
        ).exists()
        self.assertFalse(is_existed)

        # first call main
        response = self.authenticated_manager_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tip_rating = TipRating.objects.filter(
            added_by=self.manager_user, tip=self.tip1
        ).first()

        self.assertEqual(tip_rating.read_count, 1)

        # second call main
        response = self.authenticated_manager_client.get(self.detail_url)

        tip_rating.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tip_rating.read_count, 2)

    def test_try_tip_success(self):
        response = self.authenticated_dlp_client.post(self.try_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.tip_rating1.refresh_from_db()
        self.assertEqual(self.tip_rating1.try_count, 3)

    def test_try_tip_success_with_student(self):
        tip_rating = TipRatingFactory.create(
            added_by=self.experimental_user,
            tip=self.tip3,
            student=self.student,
            read_count=1,
            try_count=2,
            clarity=1,
            relevance=2,
            uniqueness=3,
        )

        data = {"student": self.student.id}

        response = self.authenticated_dlp_client.post(self.try_url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        tip_rating.refresh_from_db()
        self.assertEqual(tip_rating.try_count, 3)

    def test_try_tip_success_with_helpful_is_false(self):
        data = {"helpful": False}

        response = self.authenticated_dlp_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        old_count = self.tip3.helpful_count
        self.tip3.refresh_from_db()
        self.assertEqual(old_count, self.tip3.helpful_count)

    def test_try_tip_success_with_helpful_is_true(self):
        data = {"helpful": True}

        response = self.authenticated_dlp_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        old_count = self.tip3.helpful_count
        self.tip3.refresh_from_db()
        self.assertEqual(old_count + 1, self.tip3.helpful_count)

    def test_try_tip_success_with_retry_later_is_false(self):
        data = {"retry_later": False}

        response = self.authenticated_dlp_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.tip_rating1.refresh_from_db()
        self.assertFalse(self.tip_rating1.retry_later)

    def test_try_tip_success_with_retry_later_is_true(self):
        self.tip_rating1.retry_later = False
        self.tip_rating1.save()

        data = {"retry_later": True}

        response = self.authenticated_dlp_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.tip_rating1.refresh_from_db()
        self.assertTrue(self.tip_rating1.retry_later)

    def test_try_tip_success_with_guest(self):
        response = self.authenticated_guest_client.post(self.try_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.tip_rating3.refresh_from_db()
        self.assertEqual(self.tip_rating3.try_count, 5)

    def test_try_tip_success_with_guest_and_helpful_is_false(self):
        data = {"helpful": False}

        response = self.authenticated_guest_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        old_count = self.tip3.helpful_count
        self.tip3.refresh_from_db()
        self.assertEqual(old_count, self.tip3.helpful_count)

    def test_try_tip_success_with_guest_and_helpful_is_true(self):
        data = {"helpful": True}

        response = self.authenticated_guest_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        old_count = self.tip3.helpful_count
        self.tip3.refresh_from_db()
        self.assertEqual(old_count + 1, self.tip3.helpful_count)

    def test_try_tip_success_with_guest_and_retry_later_is_false(self):
        data = {"retry_later": False}

        response = self.authenticated_guest_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.tip_rating3.refresh_from_db()
        self.assertFalse(self.tip_rating3.retry_later)

    def test_try_tip_success_with_guest_and_retry_later_is_true(self):
        self.tip_rating3.retry_later = False
        self.tip_rating3.save()

        data = {"retry_later": True}

        response = self.authenticated_guest_client.post(
            self.try_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.tip_rating3.refresh_from_db()
        self.assertTrue(self.tip_rating3.retry_later)

    def test_try_tip_success_with_check_try_tip_notification(self):
        response = self.authenticated_dlp_client.post(self.try_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.tip_rating1.refresh_from_db()
        self.assertEqual(self.tip_rating1.try_count, 3)

        # check create notification
        is_existed = Notification.objects.filter(
            actor_object_id=self.experimental_user.id,
            recipient_id=self.experimental_user.id,
            verb=constants.Activity.TRY_TIP,
            description="{} tried the tip {}".format(
                self.tip_rating1.added_by.full_name,
                self.tip_rating1.tip.title,
            ),
        ).exists()
        self.assertTrue(is_existed)
