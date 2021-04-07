import os
import sys
import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from django.db import connection
from django.utils import timezone

from random import randrange, choice, shuffle, random, choices
from datetime import datetime, timedelta
from loremipsum import Generator
from english_words import english_words_set

from sis.models import Profile, Message, SemesterStudent, Student, Semester

loremgen = Generator(dictionary=english_words_set)
def get_sentence():
    (w,s,text) = loremgen.generate_sentence()
    return text
def get_paragraph():
    (w,s,text) = loremgen.generate_paragraph()
    return text



# for every student, 1-3 messages. and some replies
def rand_between(timedate1, timedate2):
    aDate = timedate1 + random() * (timedate2 - timedate1)
    aDateTime = datetime.combine(aDate, datetime.min.time()) + timedelta(
        minutes=480 + randrange(1, 12 * 60))
    aDateTime = timezone.make_aware(aDateTime)
    return aDateTime

def createData():
    to_generate = 3
    error_count = 0
    student_profiles = Profile.objects.filter(role=Profile.ACCESS_STUDENT)
    admin_profiles = list(Profile.objects.filter(role=Profile.ACCESS_ADMIN))

    midnight = datetime.min.time()
    for profile in student_profiles:
        if not profile.has_student():
            print(f'ERROR {profile.user.username} ({profile}) is a student but with no profile')
            continue

        student = profile.student
        message_count = randrange(randrange(1, to_generate))
        semestersstuds = list(student.semesterstudent_set.all())
        shuffle(semestersstuds)

        if len(semestersstuds) == 0:
            continue

        for ix in range(1, randrange(1, to_generate)):
            aSemester = choice(semestersstuds).semester

            if random() < 0.4:
                anAdmin = choice(admin_profiles)
                when = rand_between(aSemester.date_started, aSemester.date_ended)

                subject = get_sentence()
                body = get_paragraph()
                msg = Message.objects.create(sender=profile,recipient=anAdmin,
                                             time_sent=when,
                                             subject=subject,
                                             body=body)
                print(f'From {msg}')
                if random() < 0.9:
                    msg.time_read = when + timedelta(days=random())
                    msg.save()

                    if random() < 0.75:
                        response_at = msg.time_read + timedelta(days=random()/2)
                        subject = get_sentence()
                        body = get_paragraph()
                        response = Message.objects.create(sender=anAdmin,recipient=profile,
                                                      time_sent=response_at,
                                                          subject="But "+subject,
                                                          body=body,
                                                          in_response_to=msg)
                        print(f'   -> Resp {response}')

            if random() < 0.1:
                anAdmin = choice(admin_profiles)
                when = rand_between(aSemester.date_started, aSemester.date_ended)
                body = get_paragraph()
                msg = Message.objects.create(sender=anAdmin,
                                             recipient=profile,
                                             time_sent=when,
                                             subject="You're in trouble",
                                             body=body,
                                             high_priority=True)
                if random() < 0.3:
                    msg.time_read = when + timedelta(days=random())
                    msg.save()
                print(f'Alert {msg}')

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_message')


if __name__ == "__main__":
    createData()
