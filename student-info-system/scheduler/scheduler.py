from django.utils import timezone

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from config import settings
from sis.models import Task


class TaskScheduler:

    scheduler = None

    def add_jobs(self, tasks):
        print("in add jobs")
        for task in tasks:
            if task.frequency_type == Task.FREQUENCY_TYPES.DATE:
                self.scheduler.add_job(task.execute(), task.frequency_type, task.date)
            elif task.frequency_type == Task.FREQUENCY_TYPES.INTERVAL:
                self.scheduler.add_job(task.execute(), task.frequency_type, **task.interval.create_kw_dict())
            else:
                self.scheduler.add_job(task.execute())

    def start(self):
        if self.scheduler == None:
            scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
            scheduler.add_jobstore(DjangoJobStore(), 'default')

        tasks = Task.objects.filter(active=True)
        self.add_jobs(tasks)

        self.scheduler.start()
