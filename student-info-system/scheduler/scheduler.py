from django.utils import timezone

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from config import settings
from sis.models import Tasks, Task


class TaskScheduler:
    scheduler = None

    def add_jobs(self, tasks):
        for task in tasks:
            job_dict = task.create_job_dict()
            TaskScheduler.scheduler.scheduled_job(job_dict)

    def pause_jobs(self, tasks):
        for task in tasks:
            TaskScheduler.scheduler.pause_job(task.job_id, 'default')

    def start(self):
        if TaskScheduler.scheduler is None:
            TaskScheduler.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
            TaskScheduler.scheduler.add_jobstore(DjangoJobStore(), 'default')

        tasks = Tasks.objects.all()
        jobs = [x.task for x in tasks if x.task.active is True]
        inactive_jobs = [x.task for x in tasks if x.task.active is False]
        self.add_jobs(jobs)
        self.pause_jobs(inactive_jobs)

        TaskScheduler.scheduler.start()
