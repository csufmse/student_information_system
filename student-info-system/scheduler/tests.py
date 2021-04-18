from django.test import TestCase

from sis.models import AcademicProbationTask, Interval, Tasks
from .scheduler import TaskScheduler


class TaskSchedulerTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        interval = Interval.objects.create(interval_amount=20, interval_type=Interval.SECONDS)
        cls.APT = AcademicProbationTask.objects.create(
            interval=interval,
            frequency_type=AcademicProbationTask.INTERVAL,
            description='aptask test')
        cls.tasks = Tasks.add_task(cls.APT)

    def test_scheduler_adds_jobs(self):
        task_scheduler = TaskScheduler()
        task_scheduler.start()


# replace_existing=True
