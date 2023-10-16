from tests.base_test import BaseTestCase
from tests.factories import ActivityFactory


class TestActivity(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.activity = ActivityFactory.build(user=cls.normal_user)

    def test_can_modify(self):
        # False
        self.assertFalse(self.activity.can_modify(self.experimental_user))

        # True
        self.assertTrue(self.activity.can_modify(self.normal_user))
        self.assertTrue(self.activity.can_modify(self.manager_user))
