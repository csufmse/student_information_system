from django.test import TestCase

from sis.models import AcademicProbationTask, Interval, Tasks, Task


class TasksTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        interval = Interval.objects.create(interval_amount=20,
                                           interval_type=Interval.SECONDS)
        cls.APT = AcademicProbationTask.objects.create(interval=interval,
                                                       frequency_type=AcademicProbationTask.INTERVAL,
                                                       title='AP Task1',
                                                       description='ap task test')
        cls.tasks = Tasks.add_task(cls.APT)

    def test_APT_name(self):
        self.assertEqual(TasksTestCase.APT.name, 'AP Task1')

    def test_APT_job_id(self):
        pk = str(TasksTestCase.APT.pk)
        job_id = "AcademicProbationTask" + pk
        self.assertEqual(TasksTestCase.APT.job_id, job_id)
       
    def  test_tasks_APT_connection(self):
        self.assertEqual(TasksTestCase.tasks.task.name, 'AP Task1')
