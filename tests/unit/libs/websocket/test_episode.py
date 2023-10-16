from notifications.models import Notification

import constants
from libs.websocket import EpisodeNotificationWebsocket
from tests.base_test import BaseTestCase
from tests.factories import (
    EpisodeFactory,
    StudentFactory,
    UserStudentMappingFactory,
)


class TestEpisodeNotificationWebsocket(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student = StudentFactory.create()

        UserStudentMappingFactory.create(
            student=cls.student,
            user=cls.manager_user,
            added_by=cls.super_user,
        )
        UserStudentMappingFactory.create(
            student=cls.student,
            user=cls.experimental_user,
            added_by=cls.super_user,
        )

        cls.episode = EpisodeFactory.create(
            student=cls.student,
            user=cls.manager_user,
        )

    def test_send_episode_notification_to_mapped_users(self):
        old_count = Notification.objects.filter(
            verb=constants.Activity.CREATE_EPISODE
        ).count()

        EpisodeNotificationWebsocket.send_episode_notification_to_mapped_users(
            self.episode
        )

        new_count = Notification.objects.filter(
            verb=constants.Activity.CREATE_EPISODE
        ).count()
        self.assertEqual(old_count + 1, new_count)
