from django.urls import reverse
from rest_framework import status
from reversion.models import Version

import constants
from main.models import Example
from tests.base_api_test import BaseAPITestCase
from tests.factories import ExampleFactory, TagFactory, TaggedExampleFactory


class TestExampleAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.list_url = reverse("v1:examples-list")

        cls.example1 = ExampleFactory.create(description="example 1")
        cls.example2 = ExampleFactory.create(description="example 2")

        # tags
        cls.tag1 = TagFactory.create(name="name_1", slug="slug_1")
        cls.tag2 = TagFactory.create(name="name_2", slug="slug_2")
        TaggedExampleFactory.create(content_object=cls.example1, tag=cls.tag1)
        TaggedExampleFactory.create(content_object=cls.example2, tag=cls.tag2)

        cls.detail_url = reverse("v1:examples-detail", args=[cls.example1.id])
        cls.versions_url = reverse(
            "v1:examples-versions", args=[cls.example1.id]
        )
        cls.recover_url = reverse(
            "v1:examples-recover", args=[cls.example1.id]
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
            "episode",
            "is_active",
            "goal",
            "is_workflow_completed",
            "is_bookmarked",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
            "average_rating",
            "clarity_average_rating",
            "recommended_average_rating",
            "tags",
            "student_ids",
            "episode_student_id",
        ]
        cls.expected_list_keys = [
            "id",
            "tip",
            "description",
            "example_type",
            "context_notes",
            "sounds_like",
            "looks_like",
            "updated_by",
            "episode",
            "is_active",
            "goal",
            "is_workflow_completed",
            "is_bookmarked",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
            "episode_student_id",
        ]

    def test_get_list_success(self):
        response = self.forced_authenticated_client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)

        example_data = response.data["results"][0]
        self.assertEqual(
            sorted(self.expected_list_keys), sorted(example_data.keys())
        )

    def test_get_list_success_with_filter_tag(self):
        # tag = tag1.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": self.tag1.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertNotIn(self.example2.id, ids)

        # tag = tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": self.tag2.name},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.example1.id, ids)
        self.assertIn(self.example2.id, ids)

        # tag = tag1.name, tag2.name
        response = self.authenticated_manager_client.get(
            self.list_url,
            {"tag": "{},{}".format(self.tag1.name, self.tag2.name)},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

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

    def test_get_list_with_filter_episode(self):
        # episode_id is from example 1
        response = self.forced_authenticated_client.get(
            self.list_url, {"episode": self.example1.episode_id}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_keys = ["count", "next", "previous", "results"]
        self.assertEqual(sorted(expected_keys), sorted(response.data.keys()))

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.example1.id, ids)
        self.assertNotIn(self.example2.id, ids)

        # episode_id is from example 2
        response = self.forced_authenticated_client.get(
            self.list_url, {"episode": self.example2.episode_id}
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

    def test_get_detail_success_check_tags(self):
        # add tag
        TaggedExampleFactory.create(
            content_object=self.example1, tag=self.tag2
        )

        response = self.forced_authenticated_client.get(self.detail_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.expected_detail_keys), sorted(response.data.keys())
        )

        self.assertListEqual(["name_1", "name_2"], response.data["tags"])

    def test_get_detail_not_found(self):
        not_found_url = reverse("v1:examples-detail", args=[-1])
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
            "is_bookmarked": True,
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
            "is_bookmarked": True,
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
        self.assertNotEqual(
            self.normal_user.id, response.data["added_by"]["id"]
        )
        self.assertNotEqual(
            self.normal_user.full_name,
            response.data["added_by"]["full_name"],
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
            reverse("v1:examples-detail", args=[example3.id])
        )

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        response = self.forced_authenticated_client.get(
            reverse("v1:examples-detail", args=[example3.id])
        )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_delete_fail(self):
        response = self.forced_authenticated_client.delete(
            reverse("v1:examples-detail", args=[-1])
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
            "episode": self.example1.episode_id,
            "is_active": True,
            "goal": "hello",
            "is_workflow_completed": True,
            "is_bookmarked": True,
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

        self.assertEqual(
            self.normal_user.id, response.data["updated_by"]["id"]
        )
        self.assertEqual(
            self.normal_user.full_name,
            response.data["updated_by"]["full_name"],
        )
        self.assertEqual(self.normal_user.id, response.data["added_by"]["id"])
        self.assertEqual(
            self.normal_user.full_name,
            response.data["added_by"]["full_name"],
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
            "episode": self.example1.episode_id,
            "is_active": True,
            "goal": "hello",
            "is_workflow_completed": True,
            "is_bookmarked": True,
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

    def test_create_new_version_when_create_success(self):
        data = {
            "tip": self.example1.tip_id,
            "description": "new example",
            "example_type": constants.ExampleType.ANECDOTAL_TYPE,
            "context_notes": "",
            "sounds_like": "",
            "looks_like": "",
            "episode": self.example1.episode_id,
            "is_active": True,
            "goal": "hello",
            "is_workflow_completed": True,
            "is_bookmarked": True,
            "headline": "aaaaaa",
            "heading": "heading",
            "situation": "aaaaaa",
            "shadows_response": "aaaaa",
            "outcome": "aaaaaa",
        }

        response = self.forced_authenticated_client.post(
            self.list_url, data=data, format="json"
        )
        example_id = response.data["id"]
        example = Example.objects.get(pk=example_id)
        version = Version.objects.get_for_object(example).first()
        example_field_dict = version.field_dict
        example_field_dict["tip"] = example_field_dict.pop("tip_id")
        example_field_dict["episode"] = example_field_dict.pop("episode_id")
        reversion = version.revision

        for key in data.keys():
            self.assertEqual(example_field_dict[key], response.data[key])

        self.assertEqual("", reversion.comment)
        self.assertEqual(self.normal_user.id, reversion.user_id)

    def test_create_new_version_when_update_tip_success(self):
        data = {"description": "new description"}

        response = self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        example_id = response.data["id"]
        example = Example.objects.get(pk=example_id)
        version = Version.objects.get_for_object(example).first()
        example_field_dict = version.field_dict
        reversion = version.revision

        for key in data.keys():
            self.assertEqual(example_field_dict[key], data[key])

        self.assertEqual("", reversion.comment)
        self.assertEqual(self.normal_user.id, reversion.user_id)

    def test_get_versions_success_with_manager_user(self):
        data = {"description": "new description"}

        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        versions = Version.objects.get_for_object(self.example1)
        example_ids = [version.field_dict.get("id") for version in versions]

        # check with role admin
        response = self.authenticated_admin_client.get(self.versions_url)
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual(example_ids, expected_value)

        # check with role manager
        response = self.authenticated_manager_client.get(self.versions_url)
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual(example_ids, expected_value)

    def test_get_versions_with_filter_success_with_manager_user(self):
        data = {"description": "new description"}

        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )
        version = Version.objects.get_for_object(self.example1).first()
        example_ids = version.field_dict.get("id")

        filter_data = {"version": version.id}

        # check with role admin
        response = self.authenticated_admin_client.get(
            self.versions_url, data=filter_data
        )
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual([example_ids], expected_value)

        # check with role manager
        response = self.authenticated_manager_client.get(
            self.versions_url, data=filter_data
        )
        expected_value = [item["id"] for item in response.data]

        self.assertListEqual([example_ids], expected_value)

    def test_recover_with_not_params_success_with_admin_user(self):
        data = {"description": "new description"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"description": "new description 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        response = self.authenticated_admin_client.post(self.recover_url)
        self.example1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new description", self.example1.description)

    def test_recover_with_params_success_with_admin_user(self):
        data = {"description": "new description"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"description": "new description 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"description": "new description 2"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        version = Version.objects.get_for_object(self.example1)[2]
        response = self.authenticated_admin_client.post(
            self.recover_url, data={"version": version.id}
        )
        self.example1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new description", self.example1.description)

    def test_recover_with_not_params_success_with_manager_user(self):
        data = {"description": "new description"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"description": "new description 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        response = self.authenticated_manager_client.post(self.recover_url)
        self.example1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new description", self.example1.description)

    def test_recover_with_params_success_with_manager_user(self):
        data = {"description": "new description"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"description": "new description 1"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        data = {"description": "new description 2"}
        self.forced_authenticated_client.patch(
            self.detail_url, data=data, format="json"
        )

        version = Version.objects.get_for_object(self.example1)[2]
        response = self.authenticated_manager_client.post(
            self.recover_url, data={"version": version.id}
        )
        self.example1.refresh_from_db()

        self.assertEqual(response.data["message"], "Success")
        self.assertEqual("new description", self.example1.description)

    def test_get_versions_fail_with_normal_user(self):
        response = self.forced_authenticated_client.get(self.versions_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recover_fail_with_normal_user(self):
        response = self.forced_authenticated_client.get(self.versions_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
