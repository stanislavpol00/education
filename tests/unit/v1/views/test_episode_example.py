from django.urls import reverse
from rest_framework import status

import constants
from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory


class TestEpisodeExampleAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.example1 = ExampleFactory.create(description="example 1")
        cls.episode = cls.example1.episode
        cls.example2 = ExampleFactory.create(
            description="example 2", episode=cls.episode
        )

        cls.list_url = reverse(
            "v1:episode-examples-list", args=[cls.episode.id]
        )
        cls.detail_url = reverse(
            "v1:episode-examples-detail",
            args=[cls.episode.id, cls.example1.id],
        )

        cls.expected_detail_keys = [
            "id",
            "tip",
            "description",
            "example_type",
            "context_notes",
            "sounds_like",
            "looks_like",
            "updated_by",
            "updated",
            "episode",
            "is_active",
            "goal",
            "is_workflow_completed",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)

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

    def test_get_list_with_filter_description(self):
        # description = example 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"description": "example 1"}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertNotIn(self.example2.id, ids)

        # description example X
        response = self.forced_authenticated_client.get(
            self.list_url, {"description": "example X"}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example1.id, ids)
        self.assertNotIn(self.example2.id, ids)

    def test_get_list_with_filter_is_active(self):
        # is_active = True
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": True}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)

        # is_active = False
        response = self.forced_authenticated_client.get(
            self.list_url, {"is_active": False}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example1.id, ids)
        self.assertNotIn(self.example2.id, ids)

    def test_get_list_with_filter_tip(self):
        # tip is from example 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"tip": self.example1.tip_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertNotIn(self.example2.id, ids)

        # tip is from example 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"tip": self.example2.tip_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)

    def test_get_list_with_filter_updated_by(self):
        # updated_by_id is from example 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"updated_by": self.example1.updated_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertNotIn(self.example2.id, ids)

        # updated_by_id is from example 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"updated_by": self.example2.updated_by_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)

    def test_get_detail_success(self):
        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.example1.id, response.data["id"])

    def test_get_detail_not_found(self):
        not_found_url = reverse(
            "v1:episode-examples-detail", args=[self.episode.id, -1]
        )
        response = self.forced_authenticated_client.get(not_found_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_with_full_detail_success(self):
        data = {
            "tip": self.example1.tip_id,
            "description": "aaaaaa\n\naaaaa\n\naaaaaa",
            "example_type": constants.ExampleType.ANECDOTAL_TYPE,
            "context_notes": "",
            "sounds_like": "",
            "looks_like": "",
            "episode": self.example1.episode_id,
            "is_active": True,
            "goal": "hello",
            "is_workflow_completed": True,
            "headline": "aaaaaa",
            "heading": "heading",
            "situation": "aaaaaa",
            "shadows_response": "aaaaa",
            "outcome": "aaaaaa",
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.example1.id, response.data["id"])
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
            "tip": -1,
            "description": "aaaaaa\n\naaaaa\n\naaaaaa",
            "example_type": constants.ExampleType.ANECDOTAL_TYPE,
            "context_notes": "",
            "sounds_like": "",
            "looks_like": "",
            "updated": "2021-07-12T14:46:24.030780Z",
            "episode": self.example1.episode_id,
            "is_active": True,
            "goal": "hello",
            "is_workflow_completed": True,
            "headline": "aaaaaa",
            "heading": "heading",
            "situation": "aaaaaa",
            "shadows_response": "aaaaa",
            "outcome": "aaaaaa",
        }

        response = self.forced_authenticated_client.put(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("tip", response.data)

    def test_update_with_partial_detail(self):
        data = {
            "headline": "aaaaaa",
            "heading": "heading",
            "situation": "aaaaaa",
            "shadows_response": "aaaaa",
            "outcome": "aaaaaa",
        }

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertEqual(self.example1.id, response.data["id"])
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
        data = {"example_type": "not-existed"}

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("example_type", response.data)

    def test_delete_success(self):
        example3 = ExampleFactory.create(description="example 3")

        response = self.forced_authenticated_client.delete(
            reverse(
                "v1:episode-examples-detail",
                args=[example3.episode_id, example3.id],
            )
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.forced_authenticated_client.get(
            reverse(
                "v1:episode-examples-detail",
                args=[example3.episode_id, example3.id],
            )
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:episode-examples-detail", args=[self.episode.id, -1])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_success(self):
        data = {
            "tip": self.example1.tip_id,
            "description": "new example",
            "example_type": constants.ExampleType.ANECDOTAL_TYPE,
            "context_notes": "",
            "sounds_like": "",
            "looks_like": "",
            "is_active": True,
            "goal": "hello",
            "is_workflow_completed": True,
            "headline": "aaaaaa",
            "heading": "heading",
            "situation": "aaaaaa",
            "shadows_response": "aaaaa",
            "outcome": "aaaaaa",
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

        self.assertEqual(self.episode.id, response.data["episode"])
        self.assertEqual(
            self.normal_user.id, response.data["updated_by"]["id"]
        )
        self.assertEqual(
            self.normal_user.full_name,
            response.data["updated_by"]["full_name"],
        )

    def test_create_fail(self):
        data = {
            "tip": -1,
            "description": "new example",
            "example_type": constants.ExampleType.ANECDOTAL_TYPE,
            "context_notes": "",
            "sounds_like": "",
            "looks_like": "",
            "updated": "2021-07-12T14:46:24.030780Z",
            "is_active": True,
            "goal": "hello",
            "is_workflow_completed": True,
            "headline": "aaaaaa",
            "heading": "heading",
            "situation": "aaaaaa",
            "shadows_response": "aaaaa",
            "outcome": "aaaaaa",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        self.assertIn("tip", response.data)
