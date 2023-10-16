from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from notifications.models import Notification
from rest_framework import status

import constants
from main.models import Example, Tip
from tests.base_api_test import BaseAPITestCase
from tests.factories import (
    ExampleFactory,
    TipFactory,
    UserFactory,
    UserStudentMappingFactory,
)


class TestManagerUserGridAPI(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        content_types = ContentType.objects.get_for_models(
            Tip, Example
        )
        tip_content_type = content_types[Tip].id
        example_content_type = content_types[Example].id

        cls.user_grid_url = reverse("v1:managers-users-grid")

        cls.first_user = UserFactory.create(first_name="123", last_name="abc")

        cls.tip1 = TipFactory.create(
            title="tip 1",
            description="description 1",
            added_by=cls.normal_user,
            updated_by=None,
        )
        cls.tip1.created_at -= timezone.timedelta(hours=24)
        cls.tip1.save()

        tip1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.tip1.id,
                action_object_content_type_id=tip_content_type,
                recipient=cls.normal_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        tip1_notification.timestamp -= timezone.timedelta(hours=24)
        tip1_notification.save()

        cls.tip2 = TipFactory.create(
            title="tip 2",
            description="description 2",
            added_by=cls.normal_user,
            updated_by=None,
        )

        cls.example1 = ExampleFactory.create(
            description="example 1",
            added_by=cls.normal_user,
            tip=None,
            episode=None,
            updated_by=None,
        )
        cls.example1.created_at -= timezone.timedelta(hours=24)
        cls.example1.save()

        example1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.example1.id,
                action_object_content_type_id=example_content_type,
                recipient=cls.normal_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        example1_notification.timestamp -= timezone.timedelta(hours=24)
        example1_notification.save()

        cls.example2 = ExampleFactory.create(
            description="example 2",
            added_by=cls.normal_user,
            tip=None,
            episode=None,
            updated_by=None,
        )

        cls.old_example = ExampleFactory.create(
            added_by=cls.normal_user, tip=None, episode=None, updated_by=None
        )
        cls.old_example.created_at -= timezone.timedelta(days=365)
        cls.old_example.save()

        old_example_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.old_example.id,
                action_object_content_type_id=example_content_type,
                recipient=cls.normal_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        old_example_notification.timestamp -= timezone.timedelta(days=365)
        old_example_notification.save()

        # of admin and manager
        cls.tip3 = TipFactory.create(
            title="tip 3 of admin and manager",
            description="description 3 of admin and manager",
            added_by=cls.manager_user,
            updated_by=None,
        )
        cls.tip3.created_at -= timezone.timedelta(hours=24)
        cls.tip3.save()

        tip3_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.tip3.id,
                action_object_content_type_id=tip_content_type,
                recipient=cls.manager_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        tip3_notification.timestamp -= timezone.timedelta(hours=24)
        tip3_notification.save()

        cls.tip4 = TipFactory.create(
            title="tip 4 of admin and manager",
            description="description 4 of admin and manager",
            added_by=cls.manager_user,
            updated_by=None,
        )

        cls.example3 = ExampleFactory.create(
            description="example 3 of admin and manager",
            added_by=cls.manager_user,
            tip=None,
            episode=None,
            updated_by=None,
        )
        cls.example3.created_at -= timezone.timedelta(hours=24)
        cls.example3.save()

        example3_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.example3.id,
                action_object_content_type_id=example_content_type,
                recipient=cls.manager_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        example3_notification.timestamp -= timezone.timedelta(hours=24)
        example3_notification.save()

        cls.example4 = ExampleFactory.create(
            description="example 4 of admin and manager",
            added_by=cls.manager_user,
            tip=None,
            episode=None,
            updated_by=None,
        )

        cls.old_example1 = ExampleFactory.create(
            added_by=cls.manager_user, tip=None, episode=None, updated_by=None
        )
        cls.old_example1.created_at -= timezone.timedelta(days=365)
        cls.old_example1.save()

        old_example1_notification = (
            Notification.objects.filter(
                action_object_object_id=cls.old_example1.id,
                action_object_content_type_id=example_content_type,
                recipient=cls.manager_user,
                level="success",
            )
            .order_by("-timestamp")
            .first()
        )
        old_example1_notification.timestamp -= timezone.timedelta(days=365)
        old_example1_notification.save()

        cls.pagination_keys = [
            "count",
            "next",
            "previous",
            "results",
        ]

        cls.user_grid_keys = [
            "practitioner",
            "tips",
            "examples",
        ]

        cls.practitioner_keys = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "last_activity",
            "assigned_students",
        ]

        cls.assigned_student_keys = [
            "id",
            "first_name",
            "last_name",
            "nickname",
            "is_active",
            "image",
            "visible_for_guest",
            "created_at",
            "updated_at",
        ]

        cls.tip_keys = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "contributed_at",
        ]

        cls.example_keys = [
            "id",
            "tip",
            "description",
            "example_type",
            "context_notes",
            "sounds_like",
            "looks_like",
            "episode",
            "is_active",
            "goal",
            "is_workflow_completed",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
            "updated_by",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
            "contributed_at",
        ]

    def test_get_success_manager_user_check_keys(self):
        # check with manager_user because it has data
        data_params = {"role": constants.Role.MANAGER}
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=data_params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        # get one item to check
        user_grid = response.data["results"][0]
        user_grid_keys = list(user_grid.keys())
        self.assertEqual(sorted(user_grid_keys), sorted(self.user_grid_keys))

        practitioner_keys = list(user_grid["practitioner"].keys())
        self.assertEqual(
            sorted(practitioner_keys), sorted(self.practitioner_keys)
        )

        tip_keys = list(
            set().union(*(tip.keys() for tip in user_grid["tips"]))
        )
        self.assertEqual(sorted(tip_keys), sorted(self.tip_keys))

        example_keys = list(
            set().union(*(example.keys() for example in user_grid["examples"]))
        )
        self.assertEqual(sorted(example_keys), sorted(self.example_keys))

    def test_get_list_success_manager_user(self):
        response = self.authenticated_manager_client.get(
            self.user_grid_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        normal_user_tips_id = []
        normal_user_examples_id = []

        manager_user_tips_id = []
        manager_user_examples_id = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.normal_user.id:
                normal_user_tips_id = [tip["id"] for tip in item["tips"]]
                normal_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]
            elif user_id == self.manager_user.id:
                manager_user_tips_id = [tip["id"] for tip in item["tips"]]
                manager_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

        # check for normal user
        self.assertIn(self.tip1.id, normal_user_tips_id)
        self.assertIn(self.tip2.id, normal_user_tips_id)

        self.assertIn(self.example1.id, normal_user_examples_id)
        self.assertIn(self.example2.id, normal_user_examples_id)
        self.assertIn(self.old_example.id, normal_user_examples_id)

        # check for manager user
        self.assertIn(self.tip3.id, manager_user_tips_id)
        self.assertIn(self.tip4.id, manager_user_tips_id)

        self.assertIn(self.example3.id, manager_user_examples_id)
        self.assertIn(self.example4.id, manager_user_examples_id)
        self.assertIn(self.old_example1.id, manager_user_examples_id)

    def test_get_list_success_manager_user_with_filter_ordering(self):
        user1 = UserFactory.create(first_name="testfullname_A")
        user2 = UserFactory.create(first_name="testfullname_B")

        # only filter user1 and user2, order full_name ascending
        data_params = {
            "full_name": "testfullname_",
            "ordering": "full_name",
        }
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=data_params, format="json"
        )

        users_grids = response.data["results"]
        user_ids = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_ids.append(practitioner["id"])

        self.assertEqual(user_ids[0], user1.id)
        self.assertEqual(user_ids[1], user2.id)

        # only filter user1 and user2,  order full_name descending
        data_params = {
            "full_name": "testfullname_",
            "ordering": "-full_name",
        }
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=data_params, format="json"
        )

        users_grids = response.data["results"]
        user_ids = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_ids.append(practitioner["id"])

        self.assertEqual(user_ids[0], user2.id)
        self.assertEqual(user_ids[1], user1.id)

    def test_get_success_manager_user_with_filter_start_date(self):
        date_params = {
            "start_date": timezone.now() - timezone.timedelta(days=5),
            "limit": 100,
        }
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=date_params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        normal_user_tips_id = []
        normal_user_examples_id = []

        manager_user_tips_id = []
        manager_user_examples_id = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.normal_user.id:
                normal_user_tips_id = [tip["id"] for tip in item["tips"]]
                normal_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]
            elif user_id == self.manager_user.id:
                manager_user_tips_id = [tip["id"] for tip in item["tips"]]
                manager_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

        # check for normal user
        self.assertIn(self.tip1.id, normal_user_tips_id)
        self.assertIn(self.tip2.id, normal_user_tips_id)

        self.assertIn(self.example1.id, normal_user_examples_id)
        self.assertIn(self.example2.id, normal_user_examples_id)
        self.assertNotIn(self.old_example.id, normal_user_examples_id)

        # check for manager user
        self.assertIn(self.tip3.id, manager_user_tips_id)
        self.assertIn(self.tip4.id, manager_user_tips_id)

        self.assertIn(self.example3.id, manager_user_examples_id)
        self.assertIn(self.example4.id, manager_user_examples_id)
        self.assertNotIn(self.old_example1.id, manager_user_examples_id)

    def test_get_success_manager_user_with_filter_end_date(self):
        date_params = {
            "end_date": timezone.now() - timezone.timedelta(days=5),
            "limit": 100,
        }
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=date_params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        normal_user_tips_id = []
        normal_user_examples_id = []

        manager_user_tips_id = []
        manager_user_examples_id = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.normal_user.id:
                normal_user_tips_id = [tip["id"] for tip in item["tips"]]
                normal_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]
            elif user_id == self.manager_user.id:
                manager_user_tips_id = [tip["id"] for tip in item["tips"]]
                manager_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

        # check for normal user
        self.assertNotIn(self.tip1.id, normal_user_tips_id)
        self.assertNotIn(self.tip2.id, normal_user_tips_id)

        self.assertNotIn(self.example1.id, normal_user_examples_id)
        self.assertNotIn(self.example2.id, normal_user_examples_id)
        self.assertIn(self.old_example.id, normal_user_examples_id)

        # check for manager user
        self.assertNotIn(self.tip3.id, manager_user_tips_id)
        self.assertNotIn(self.tip4.id, manager_user_tips_id)

        self.assertNotIn(self.example3.id, manager_user_examples_id)
        self.assertNotIn(self.example4.id, manager_user_examples_id)
        self.assertIn(self.old_example1.id, manager_user_examples_id)

    def test_get_success_manager_user_with_filter_date(self):
        date_params = {
            "start_date": timezone.now() - timezone.timedelta(days=364),
            "end_date": timezone.now() - timezone.timedelta(hours=1),
            "limit": 1000,
        }
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=date_params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        normal_user_tips_id = []
        normal_user_examples_id = []

        manager_user_tips_id = []
        manager_user_examples_id = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.normal_user.id:
                normal_user_tips_id = [tip["id"] for tip in item["tips"]]
                normal_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

            elif user_id == self.manager_user.id:
                manager_user_tips_id = [tip["id"] for tip in item["tips"]]
                manager_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

        # check for normal user
        self.assertIn(self.tip1.id, normal_user_tips_id)
        self.assertNotIn(self.tip2.id, normal_user_tips_id)

        self.assertIn(self.example1.id, normal_user_examples_id)
        self.assertNotIn(self.example2.id, normal_user_examples_id)
        self.assertNotIn(self.old_example.id, normal_user_examples_id)

        # check for manager user
        self.assertIn(self.tip3.id, manager_user_tips_id)
        self.assertNotIn(self.tip4.id, manager_user_tips_id)

        self.assertIn(self.example3.id, manager_user_examples_id)
        self.assertNotIn(self.example4.id, manager_user_examples_id)
        self.assertNotIn(self.old_example1.id, manager_user_examples_id)

    def test_get_success_manager_user_with_filter_role(self):
        params = {"role": constants.Role.MANAGER}
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=params, format="json"
        )

        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        normal_user_tips_id = []
        normal_user_examples_id = []

        manager_user_tips_id = []
        manager_user_examples_id = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.normal_user.id:
                normal_user_tips_id = [tip["id"] for tip in item["tips"]]
                normal_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

            elif user_id == self.manager_user.id:
                manager_user_tips_id = [tip["id"] for tip in item["tips"]]
                manager_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

        # check for normal user
        self.assertNotIn(self.tip1.id, normal_user_tips_id)
        self.assertNotIn(self.tip2.id, normal_user_tips_id)

        self.assertNotIn(self.example1.id, normal_user_examples_id)
        self.assertNotIn(self.example2.id, normal_user_examples_id)
        self.assertNotIn(self.old_example.id, normal_user_examples_id)

        # check for manager user
        self.assertIn(self.tip3.id, manager_user_tips_id)
        self.assertIn(self.tip4.id, manager_user_tips_id)

        self.assertIn(self.example3.id, manager_user_examples_id)
        self.assertIn(self.example4.id, manager_user_examples_id)
        self.assertIn(self.old_example1.id, manager_user_examples_id)

    def test_get_success_manager_user_with_filter_full_name(self):
        params = {"full_name": self.first_user.full_name}
        response = self.authenticated_manager_client.get(
            self.user_grid_url, data=params, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        full_names = [
            item["practitioner"]["full_name"] for item in users_grids
        ]

        self.assertIn(self.first_user.full_name, full_names)
        self.assertNotIn(self.normal_user.full_name, full_names)
        self.assertNotIn(self.manager_user.full_name, full_names)

    def test_get_success_manager_user_with_order_by_contributed(self):
        response = self.authenticated_manager_client.get(
            self.user_grid_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        normal_user_tips_id = []
        normal_user_examples_id = []

        manager_user_tips_id = []
        manager_user_examples_id = []

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.normal_user.id:
                normal_user_tips_id = [tip["id"] for tip in item["tips"]]
                normal_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

            elif user_id == self.manager_user.id:
                manager_user_tips_id = [tip["id"] for tip in item["tips"]]
                manager_user_examples_id = [
                    example["id"] for example in item["examples"]
                ]

        # check for normal user
        self.assertEqual(self.tip2.id, normal_user_tips_id[0])
        self.assertEqual(self.tip1.id, normal_user_tips_id[1])

        self.assertEqual(self.example2.id, normal_user_examples_id[0])
        self.assertEqual(self.example1.id, normal_user_examples_id[1])
        self.assertEqual(self.old_example.id, normal_user_examples_id[2])

        # check for manager user
        self.assertEqual(self.tip4.id, manager_user_tips_id[0])
        self.assertEqual(self.tip3.id, manager_user_tips_id[1])

        self.assertEqual(self.example4.id, manager_user_examples_id[0])
        self.assertEqual(self.example3.id, manager_user_examples_id[1])
        self.assertEqual(self.old_example1.id, manager_user_examples_id[2])

    def test_get_success_manager_user_check_assigned_students(self):
        user_student1 = UserStudentMappingFactory.create(
            user=self.manager_user,
            added_by=self.manager_user,
        )
        user_student2 = UserStudentMappingFactory.create(
            user=self.manager_user,
            added_by=self.manager_user,
        )

        response = self.authenticated_manager_client.get(
            self.user_grid_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        students = None

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.manager_user.id:
                students = item["practitioner"]["assigned_students"]

        assigned_student_keys = list(
            set().union(*(student.keys() for student in students))
        )
        self.assertEqual(
            sorted(assigned_student_keys), sorted(self.assigned_student_keys)
        )

        student_ids = [student["id"] for student in students]
        self.assertEqual(len(student_ids), 2)
        self.assertEqual(
            sorted([user_student1.student.id, user_student2.student.id]),
            sorted(student_ids),
        )

    def test_get_success_manager_user_check_assigned_students_empty(self):
        response = self.authenticated_manager_client.get(
            self.user_grid_url, format="json"
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            sorted(self.pagination_keys), sorted(response.data.keys())
        )

        users_grids = response.data["results"]
        students = None

        for item in users_grids:
            practitioner = item["practitioner"]
            user_id = practitioner["id"]
            if user_id == self.manager_user.id:
                students = item["practitioner"]["assigned_students"]

        self.assertEqual(students, [])

    def test_get_fail_with_check_permission(self):
        response = self.forced_authenticated_client.get(
            self.user_grid_url, format="json"
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
