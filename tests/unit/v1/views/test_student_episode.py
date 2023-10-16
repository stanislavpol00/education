from django.urls import reverse
from django.utils import timezone
from rest_framework import status

import constants
from tests.base_api_test import BaseAPITestCase
from tests.factories import EpisodeFactory, ExampleFactory


class TestStudentEpisodeAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.now = timezone.now()

        cls.episode1 = EpisodeFactory.create(
            title="episode 1",
            date=cls.now,
            full=True,
            practitioner_id=cls.experimental_user.id,
        )
        cls.student = cls.episode1.student
        cls.episode2 = EpisodeFactory.create(
            title="episode 2",
            date=cls.now - timezone.timedelta(days=2),
            full=False,
            student=cls.student,
            practitioner_id=cls.super_user.id,
        )

        cls.start_date = cls.now - timezone.timedelta(days=1)

        cls.end_date = cls.now + timezone.timedelta(days=1)

        cls.list_url = reverse(
            "v1:student-episodes-list", args=[cls.student.id]
        )
        cls.detail_url = reverse(
            "v1:student-episodes-detail",
            args=[cls.student.id, cls.episode1.id],
        )

        cls.expected_detail_keys = [
            "id",
            "student",
            "user",
            "title",
            "description",
            "description_html",
            "description_ids",
            "heads_up",
            "transcript_html",
            "transcript",
            "transcript_ids",
            "is_active",
            "date",
            "full",
            "landmark",
            "heads_up_json",
            "writers",
            "practitioner",
        ]
        cls.example1 = ExampleFactory.create(episode=cls.episode1)
        cls.tip1 = cls.example1.tip
        cls.example2 = ExampleFactory.create(episode=cls.episode2)
        cls.tip2 = cls.example2.tip

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(
            self.list_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

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

    def test_get_list_with_filter_start_date(self):
        # start_date
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"start_date": self.start_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # start_date is end_date
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"start_date": self.end_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

    def test_get_list_with_filter_end_date(self):
        # end_date = True
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"end_date": self.end_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

        # end_date = False
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"end_date": self.start_date.isoformat()},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_get_list_with_filter_title(self):
        # title = episode1
        response = self.forced_authenticated_client.get(
            self.list_url, {"title": self.episode1.title}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # title = episode2
        response = self.forced_authenticated_client.get(
            self.list_url, {"title": self.episode2.title}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

        # title = episode
        response = self.forced_authenticated_client.get(
            self.list_url, {"title": "episode"}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_get_list_with_filter_user(self):
        # user = episode1.user
        response = self.forced_authenticated_client.get(
            self.list_url, {"user": self.episode1.user_id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # user = episode2.user
        response = self.forced_authenticated_client.get(
            self.list_url, {"user": self.episode2.user_id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_get_list_with_filter_is_active(self):
        # is_active = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": False}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # is_active = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": True}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_get_list_with_filter_full(self):
        # full = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"full": False}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

        # full = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"full": True}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

    def test_get_list_with_filter_landmark(self):
        # landmark = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"landmark": False}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

        # landmark = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"landmark": True}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

    def test_get_list_with_filter_practitioner(self):
        # practitioner = episode1.practitioner
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"practitioner": self.episode1.practitioner_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # practitioner = episode2.practitioner
        response = self.forced_authenticated_client.get(
            self.list_url,
            {"practitioner": self.episode2.practitioner_id},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

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
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

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
        self.tip1.child_context = {
            constants.ChildContext.CURRENT_MOTIVATOR: "CHILD_CONTEXT_TEST",
            constants.ChildContext.ANTICIPATED_BEHAVIOR: "dddd",
        }
        self.tip1.environment_context = {
            constants.Environment.SPACE_OPPORTUNITIES: "ENVIRONMENT_CONTEXT_TEST",
            constants.Environment.SPACE_EXPECTATIONS: "new",
        }
        self.tip1.save()

        response = self.forced_authenticated_client.get(
            self.list_url,
            {"search_text": "ENVIRONMENT_CONTEXT_TEST"},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

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
        response = self.forced_authenticated_client.get(
            self.list_url, {"search_text": "CHILD_CONTEXT_TEST"}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

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
        episode = EpisodeFactory.create()
        example = ExampleFactory.create(episode=episode)
        url = reverse(
            "v1:student-episodes-detail",
            args=[episode.student_id, episode.id],
        )

        response = self.forced_authenticated_client.get(url, format="json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(episode.id, response.data["id"])
        self.assertEqual(
            example.added_by.id, response.data["writers"][0]["id"]
        )

    def test_get_detail_success_with_check_non_practitioner(self):
        episode = EpisodeFactory.create(
            title="episode 1",
            date=self.now,
            full=True,
            student=self.student,
            practitioner_id=None,
        )

        detail_url = reverse(
            "v1:student-episodes-detail",
            args=[self.student.id, episode.id],
        )

        response = self.forced_authenticated_client.get(
            detail_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(episode.id, response.data["id"])
        self.assertIsNone(response.data["practitioner"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:episodes-detail", args=[-1])
        response = self.forced_authenticated_client.get(
            not_found_url, format="json"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_success(self):
        data = {
            "student": self.episode1.student_id,
            "title": "full transcript test episode",
            "description": "hhello description",
            "description_html": "",
            "description_ids": "",
            "heads_up": "",
            "transcript_html": "",
            "transcript": "",
            "is_active": True,
            "full": False,
            "landmark": False,
            "date": "2020-07-14T15:49:39.840000Z",
            "heads_up_json": {constants.HeadsUp.PLAY_THEMES: "test"},
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.episode1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_with_partial_detail(self):
        data = {
            "title": "full transcript test episode",
            "description": "hhello description",
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.episode1.id, response.data["id"])
        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

    def test_update_partial_detail_success_with_update_practitioner(self):
        data = {"practitioner": self.manager_user.id}

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.episode1.id, response.data["id"])
        self.assertEqual(
            self.manager_user.id, response.data["practitioner"]["id"]
        )
        self.assertEqual(
            self.manager_user.full_name,
            response.data["practitioner"]["full_name"],
        )

    def test_delete_success(self):
        episode3 = EpisodeFactory.create(title="episode 3")

        response = self.forced_authenticated_client.delete(
            reverse("v1:episodes-detail", args=[episode3.id])
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.forced_authenticated_client.get(
            reverse("v1:episodes-detail", args=[episode3.id]), format="json"
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:episodes-detail", args=[-1])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_success(self):
        data = {
            "title": "new title",
            "description": "new description",
            "description_html": "",
            "description_ids": "",
            "heads_up": "",
            "transcript_html": "",
            "transcript": "",
            "is_active": True,
            "full": False,
            "landmark": False,
            "date": "2020-07-14T15:49:39.840000Z",
            "heads_up_json": {constants.HeadsUp.PLAY_THEMES: "test"},
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        for key in data.keys():
            self.assertEqual(data[key], response.data[key])

        self.assertEqual(self.normal_user.id, response.data["user"]["id"])
        self.assertEqual(
            self.normal_user.full_name, response.data["user"]["full_name"]
        )

    def test_create_success_with_check_practitioner(self):
        data = {
            "title": "new title",
            "description": "new description",
            "description_html": "",
            "description_ids": "",
            "heads_up": "",
            "transcript_html": "",
            "transcript": "",
            "is_active": True,
            "full": False,
            "landmark": False,
            "date": "2020-07-14T15:49:39.840000Z",
            "heads_up_json": {constants.HeadsUp.PLAY_THEMES: "test"},
            "practitioner": self.manager_user.id,
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.assertEqual(
            self.manager_user.id, response.data["practitioner"]["id"]
        )
        self.assertEqual(
            self.manager_user.full_name,
            response.data["practitioner"]["full_name"],
        )

    def test_create_fail(self):
        data = {
            "title": "new title",
            "description": "new description",
            "description_html": "",
            "description_ids": "",
            "heads_up": "",
            "transcript_html": "",
            "transcript": "",
            "is_active": True,
            "full": False,
            "landmark": False,
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("date", response.data)
