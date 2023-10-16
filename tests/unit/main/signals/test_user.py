from django.core.cache import cache

import constants
from main.models import Profile, User
from tests.base_test import BaseTestCase
from tests.factories import UserFactory


class TestUser(BaseTestCase):
    def test_user_creation_signal(self):
        old_profiles_count = Profile.objects.count()

        user = UserFactory.create()

        new_profiles_count = Profile.objects.count()
        self.assertEqual(old_profiles_count + 1, new_profiles_count)
        self.assertEqual(
            constants.UserType.EDUCATOR_SHADOW, user.profile.usertype
        )

    def test_user_creation_signal_with_staff_user(self):
        old_profiles_count = Profile.objects.count()

        staff_user = UserFactory.create(is_superuser=True)

        new_profiles_count = Profile.objects.count()
        self.assertEqual(old_profiles_count + 1, new_profiles_count)
        self.assertEqual(constants.UserType.ADMIN, staff_user.profile.usertype)

    def test_post_save_not_remove_managers_cache_when_create_not_role_manager(
        self,
    ):
        # cache manager
        User.objects.managers()
        value1 = cache.get(constants.Cache.MANAGER_USERS_CACHE_KEY)

        UserFactory.create(role=constants.Role.EDUCATOR_SHADOW)

        value2 = cache.get(constants.Cache.MANAGER_USERS_CACHE_KEY)

        self.assertQuerysetEqual(value1, value2, ordered=False)
