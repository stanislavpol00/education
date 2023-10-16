from django.utils import timezone

from tests.base_test import BaseTestCase
from tests.factories import (
    EpisodeFactory,
    StudentFactory,
    StudentTipFactory,
    TipFactory,
)


class TestStudent(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student = StudentFactory.create(first_name="A", last_name="B")

    def test_last_month_heads_up(self):
        student = StudentFactory.create()
        episode = EpisodeFactory.create(
            student=student,
            heads_up_json={"test": 1},
            date=timezone.localtime(),
        )
        EpisodeFactory.create(
            student=student, heads_up_json={}, date=timezone.localtime()
        )
        EpisodeFactory.create(
            student=student,
            heads_up_json={"test": 2},
            date=timezone.localtime() - timezone.timedelta(days=100),
        )

        self.assertEqual(1, len(student.last_month_heads_up))
        self.assertEqual(episode.id, student.last_month_heads_up[0]["episode"])

    def test_heads_up(self):
        student = StudentFactory.create()
        episode = EpisodeFactory.create(
            student=student,
            heads_up_json={"test": 1},
            date=timezone.localtime(),
        )
        EpisodeFactory.create(
            student=student, heads_up_json={}, date=timezone.localtime()
        )

        self.assertEqual(1, len(student.heads_up))
        self.assertEqual(episode.id, student.heads_up[0]["episode"])

    def test_str(self):
        str_student = str(self.student)

        self.assertEqual("Student: %s" % self.student.nickname, str_student)

    def test_monitoring(self):
        student = StudentFactory.create()

        self.assertIsNone(student.monitoring)

        episode = EpisodeFactory.create(
            student=student,
            heads_up_json={"test": 1, "monitoring": "hi"},
            date=timezone.localtime(),
        )

        self.assertEqual(
            episode.heads_up_json["monitoring"], student.monitoring
        )

    def test_get_full_name(self):
        expected = "A B"
        self.assertEqual(self.student.get_full_name(), expected)

    def test_full_name(self):
        expected = "A B"
        self.assertEqual(self.student.full_name, expected)

    def test_dequeue_tips(self):
        tip1 = TipFactory.create()
        tip2 = TipFactory.create()

        StudentTipFactory.create(
            student=self.student, tip=tip1, is_queued=True
        )
        StudentTipFactory.create(
            student=self.student, tip=tip2, is_queued=True
        )

        old_queued_tips_count = self.student.studenttip_set.filter(
            is_queued=True
        ).count()

        self.student.dequeue_tips(2)

        new_queued_tips_count = self.student.studenttip_set.filter(
            is_queued=True
        ).count()
        self.assertEqual(old_queued_tips_count - 2, new_queued_tips_count)
