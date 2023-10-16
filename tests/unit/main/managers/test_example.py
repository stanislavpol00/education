from django.utils import timezone

import constants
from main.models import Example
from tests.base_test import BaseTestCase
from tests.factories import ExampleFactory, UserFactory


class TestExample(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user1 = UserFactory.create(
            role=constants.Role.EXPERIMENTAL_TEACHER
        )
        cls.example1 = ExampleFactory.create(added_by=cls.user1)
        cls.example1.created_at = cls.example1.created_at - timezone.timedelta(
            hours=24
        )
        cls.example1.save()
        cls.example2 = ExampleFactory.create(added_by=cls.user1)

        cls.user2 = UserFactory.create(role=constants.Role.ADMIN_USER)
        cls.example3 = ExampleFactory.create(added_by=cls.user2)
        cls.example3.created_at = cls.example3.created_at - timezone.timedelta(
            hours=24
        )
        cls.example3.save()
        cls.example4 = ExampleFactory.create(added_by=cls.user2)

        cls.old_example = ExampleFactory.create()
        cls.old_example.created_at -= timezone.timedelta(days=10)
        cls.old_example.save()

    def test_contributions_all_users(self):
        data = Example.objects.contributions()

        self.assertEqual(5, len(data))

        user_ids = [item["added_by"] for item in data]
        self.assertIn(self.user1.id, user_ids)
        self.assertIn(self.user2.id, user_ids)

    def test_contributions_one_user(self):
        data = Example.objects.contributions(user_id=self.user1.id)

        self.assertEqual(2, len(data))
        self.assertEqual(1, data[0]["count"])
        self.assertEqual(1, data[1]["count"])

    def test_recent_with_user_id(self):
        examples = Example.objects.by_user_id(
            user_id=self.old_example.added_by_id
        )

        example_ids = [example.id for example in examples]
        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertIn(self.old_example.id, example_ids)

    def test_filter_by_params_all_users(self):
        examples = Example.objects.filter_by_params()

        example_ids = [example.id for example in examples]
        self.assertIn(self.example1.id, example_ids)
        self.assertIn(self.example2.id, example_ids)
        self.assertIn(self.example3.id, example_ids)
        self.assertIn(self.example4.id, example_ids)
        self.assertIn(self.old_example.id, example_ids)

    def test_filter_by_params_all_users_with_filter_start_date(self):
        start_date = timezone.localdate() - timezone.timedelta(days=1)
        examples = Example.objects.filter_by_params(start_date=start_date)

        example_ids = [example.id for example in examples]
        self.assertIn(self.example1.id, example_ids)
        self.assertIn(self.example2.id, example_ids)
        self.assertIn(self.example3.id, example_ids)
        self.assertIn(self.example4.id, example_ids)
        self.assertNotIn(self.old_example.id, example_ids)

    def test_filter_by_params_all_users_with_filter_end_date(self):
        end_date = timezone.localdate() - timezone.timedelta(days=5)
        examples = Example.objects.filter_by_params(end_date=end_date)

        example_ids = [example.id for example in examples]
        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertIn(self.old_example.id, example_ids)

    def test_filter_by_params_all_users_with_filter_all_date(self):
        start_date = timezone.localdate() - timezone.timedelta(days=18)
        end_date = timezone.localdate() - timezone.timedelta(days=9)
        examples = Example.objects.filter_by_params(
            start_date=start_date, end_date=end_date
        )

        example_ids = [example.id for example in examples]
        self.assertNotIn(self.example1.id, example_ids)
        self.assertNotIn(self.example2.id, example_ids)
        self.assertNotIn(self.example3.id, example_ids)
        self.assertNotIn(self.example4.id, example_ids)
        self.assertIn(self.old_example.id, example_ids)
