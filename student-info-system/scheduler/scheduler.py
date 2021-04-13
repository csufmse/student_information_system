from django.utils import timezone

import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from sis.models import Student, Message, Profile


def academic_probation_check():
    students = Student.objects.all()
    profile = Profile.objects.get(user__username='zeus')
    for student in students:
        if student.gpa() < 2.0:
            ap_message = "Your GPA has fallen below 2.0, putting you on academic probation."
            student.notify_probation(sender=profile, when=timezone.now(), body=ap_message)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(academic_probation_check, 'interval', hours=24)
    scheduler.start()
