from notifications.models import Notification

import constants
from main.models import StudentExample, StudentTip, Task
from tests.base_test import BaseTestCase
from tests.factories import (
    EpisodeFactory,
    ExampleFactory,
    StudentExampleFactory,
    StudentFactory,
    StudentTipFactory,
    TaskFactory,
)


class TestStudentExample(BaseTestCase):
    def test_post_save_signal_without_task(self):
        example = ExampleFactory.create()

        old_student_tips_count = StudentTip.objects.count()
        old_tasks_count = Task.objects.count()

        student_example = StudentExampleFactory.create(example=example)

        new_tasks_count = Task.objects.count()
        self.assertEqual(old_tasks_count, new_tasks_count)

        new_student_tips_count = StudentTip.objects.count()
        self.assertEqual(old_student_tips_count + 1, new_student_tips_count)

        latest_student_tip = StudentTip.objects.order_by("-id").first()
        self.assertEqual(student_example.example.tip, latest_student_tip.tip)
        self.assertEqual(student_example.student, latest_student_tip.student)

    def test_post_save_signal_with_task(self):
        task = TaskFactory.create(task_type=constants.TaskType.EXAMPLE)
        old_student_tips_count = StudentTip.objects.count()
        old_tasks_count = Task.objects.count()

        episode = EpisodeFactory.create(student=task.student)
        example = ExampleFactory.create(
            tip=task.tip, episode=episode, added_by=task.user
        )

        new_tasks_count = Task.objects.count()
        self.assertEqual(old_tasks_count - 1, new_tasks_count)

        new_student_tips_count = StudentTip.objects.count()
        self.assertEqual(old_student_tips_count + 1, new_student_tips_count)

        student_example = StudentExample.objects.get(
            student=task.student, example=example
        )
        latest_student_tip = StudentTip.objects.order_by("-id").first()
        self.assertEqual(student_example.example.tip, latest_student_tip.tip)
        self.assertEqual(student_example.student, latest_student_tip.student)

    def test_post_save_signal_without_task_with_existed_student_tip(self):
        existed_student_tip = StudentTipFactory.create()

        old_student_tips_count = StudentTip.objects.count()

        episode = EpisodeFactory.create(student=existed_student_tip.student)
        ExampleFactory.create(tip=existed_student_tip.tip, episode=episode)

        new_student_tips_count = StudentTip.objects.count()
        self.assertEqual(old_student_tips_count, new_student_tips_count)

    def test_post_save_by_teacher_check_send_notification(self):
        student_example = StudentExampleFactory.create()
        expected = {
            "sender_id": student_example.added_by.id,
            "recipient_id": student_example.student.added_by.id,
            "description": "A example {} is assigned to your student {}".format(
                student_example.example.headline,
                student_example.student.full_name,
            ),
            "verb": constants.Activity.ASSIGN_EXAMPLE_TO_STUDENT,
        }

        is_existed = student_example.student.added_by.notifications.filter(
            actor_object_id=str(expected["sender_id"]),
            recipient_id=str(expected["recipient_id"]),
            description=str(expected["description"]),
            verb=expected["verb"],
        )
        self.assertTrue(is_existed)

    def test_post_save_send_notification_fail_with_none_added_by(self):
        student = StudentFactory.create(added_by=None)
        student_example = StudentExampleFactory.create(student=student)
        expected_description = (
            "A example {} is assigned to your student {}".format(
                student_example.example.headline,
                student_example.student.full_name,
            )
        )
        expected_verb = constants.Activity.ASSIGN_EXAMPLE_TO_STUDENT
        is_existed = Notification.objects.filter(
            description=expected_description, verb=expected_verb
        ).exists()
        self.assertFalse(is_existed)
