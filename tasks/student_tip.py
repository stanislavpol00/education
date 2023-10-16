from celery import shared_task

from main.models import Student


@shared_task
def dequeue_student_tips(number_of_tips=2):
    students = Student.objects.all()

    for student in students:
        student.dequeue_tips(number_of_tips)
