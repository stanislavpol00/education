from django.urls import reverse
from django.utils import timezone
from rest_framework import status

import constants
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    EpisodeFactory,
    ExampleFactory,
    StudentFactory,
    TagFactory,
    TaggedEpisodeFactory,
)


class TestEpisodeAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.now = timezone.now()

        cls.list_url = reverse("v1:episodes-list")

        cls.student1 = StudentFactory.create(nickname="student1")
        cls.student2 = StudentFactory.create(nickname="student2")

        cls.episode1 = EpisodeFactory.create(
            title="episode 1",
            date=cls.now,
            full=True,
            student=cls.student1,
            practitioner_id=cls.experimental_user.id,
        )
        cls.episode2 = EpisodeFactory.create(
            title="episode 2",
            date=cls.now - timezone.timedelta(days=2),
            full=False,
            student=cls.student2,
            practitioner_id=cls.super_user.id,
        )
        cls.start_date = cls.now - timezone.timedelta(days=1)

        cls.end_date = cls.now + timezone.timedelta(days=1)

        cls.detail_url = reverse("v1:episodes-detail", args=[cls.episode1.id])

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
            "contributors",
            "tags",
            "practitioner",
            "created_at",
        ]

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

    def test_get_list_with_filter_breaking(self):
        # breaking = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"breaking": False}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # breaking = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"breaking": True}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_get_list_with_filter_only_mine(self):
        # only_mine = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"only_mine": False}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

        # only_mine = True
        my_episode = EpisodeFactory.create(user=self.normal_user)
        response = self.forced_authenticated_client.get(
            self.list_url, {"only_mine": True}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)
        self.assertIn(my_episode.id, ids)

    def test_get_list_with_filter_student(self):
        # student = student1
        response = self.forced_authenticated_client.get(
            self.list_url, {"student": self.student1.id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # student = student2
        response = self.forced_authenticated_client.get(
            self.list_url, {"student": self.student2.id}, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

    def test_get_list_success_with_filter_tag(self):
        # prepare data
        tag1 = TagFactory.create(name="name_1", slug="slug_1")
        tag2 = TagFactory.create(name="name_2", slug="slug_2")
        TaggedEpisodeFactory.create(content_object=self.episode1, tag=tag1)
        TaggedEpisodeFactory.create(content_object=self.episode1, tag=tag2)
        TaggedEpisodeFactory.create(content_object=self.episode2, tag=tag2)

        # tag = tag1.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": tag1.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertNotIn(self.episode2.id, ids)

        # tag = tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": tag2.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

        # tag = tag1.name, tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": "{},{}".format(tag1.name, tag2.name)},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.episode1.id, ids)
        self.assertIn(self.episode2.id, ids)

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

    def test_get_detail_success(self):
        example = ExampleFactory.create(episode=self.episode1)

        response = self.forced_authenticated_client.get(
            self.detail_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.episode1.id, response.data["id"])
        self.assertEqual(
            example.added_by.id, response.data["contributors"][0]["id"]
        )

    def test_get_detail_success_with_check_non_practitioner(self):
        episode = EpisodeFactory.create(
            title="episode 1",
            date=self.now,
            full=True,
            student=self.student1,
            practitioner_id=None,
        )

        detail_url = reverse("v1:episodes-detail", args=[episode.id])

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

    def test_update_with_full_detail_fail(self):
        data = {
            "student": -1,
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

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("student", response.data)

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

    def test_update_with_partial_detail_fail(self):
        data = {
            "student": -1,
            "is_active": True,
            "full": False,
            "landmark": False,
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("student", response.data)

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
            "student": self.episode2.student_id,
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
            "student": self.episode2.student_id,
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
            "student": -1,
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
            "heads_up_json": {constants.HeadsUp.PLAY_THEMES: "test"},
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("student", response.data)
