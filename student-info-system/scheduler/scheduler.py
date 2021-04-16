from django.utils import timezone

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from config import settings
from sis.models import Tasks


class TaskScheduler:
    scheduler = None

    def add_jobs(self, tasks):
        for task in tasks:
            if task.frequency_type == Task.DATE:
                TaskScheduler.scheduler.add_job(task.execute(),
                                       task.frequency_type,
                                       task.date,
                                       id=task.job_id,
                                       replace_existing=True)
            elif task.frequency_type == Task.INTERVAL:
                TaskScheduler.scheduler.add_job(task.execute(),
                                       task.frequency_type,
                                       **task.interval.create_kw_dict(),
                                       id=task.job_id,
                                       replace_existing=True)
            else:
                TaskScheduler.scheduler.add_job(task.execute(), id=task.job_id)

    def start(self):
        if TaskScheduler.scheduler == None:
            TaskScheduler.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
            TaskScheduler.scheduler.add_jobstore(DjangoJobStore(), 'default')

        tasks = Tasks.objects.all()
        jobs = [x.task for x in tasks if x.task.active == True]
        self.add_jobs(jobs)

        TaskScheduler.scheduler.start()
