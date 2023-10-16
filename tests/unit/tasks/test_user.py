from tasks.user import update_last_login, update_user_ip
from tests.base_test import BaseTestCase
from tests.factories import UserFactory


class TestUserTasks(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create()

    def test_update_last_login(self):
        last_login = self.user.last_login
        self.assertIsNone(last_login)

        update_last_login(self.user.username)

        self.user.refresh_from_db()
        new_last_login = self.user.last_login

        self.assertIsNotNone(new_last_login)
