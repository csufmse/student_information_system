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

from sis.models import Profile, Message, Major, SemesterStudent, Student, Semester

loremgen = Generator(dictionary=english_words_set)


def get_sentence():
    (w, s, text) = loremgen.generate_sentence()
    return text


def get_paragraph():
    (w, s, text) = loremgen.generate_paragraph()
    return text


# for every student, 1-3 messages. and some replies
def rand_between(timedate1, timedate2):
    aDate = timedate1 + random() * (timedate2 - timedate1)
    aDateTime = datetime.combine(
        aDate, datetime.min.time()) + timedelta(minutes=480 + randrange(1, 12 * 60))
    aDateTime = timezone.make_aware(aDateTime)
    return aDateTime


def createData():
    to_generate = 3
    error_count = 0
    student_profiles = Profile.objects.filter(role=Profile.ACCESS_STUDENT)
    admin_profiles = list(Profile.objects.filter(role=Profile.ACCESS_ADMIN))
    majors = Major.objects.all()

    for profile in student_profiles:
        if not profile.has_student():
            print(f'ERROR {profile.user.username} ({profile}) is a student but with no profile')
            continue

        student = profile.student
        semestersstuds = list(student.semesterstudent_set.all())
        shuffle(semestersstuds)

        if len(semestersstuds) == 0:
            continue

        for ix in range(1, randrange(1, to_generate)):
            aSemester = choice(semestersstuds).semester

            # change yo major
            if random() < 0.2:
                when = rand_between(aSemester.date_started, aSemester.date_ended)

                reason = get_sentence()
                to_major = choice(majors)
                mesg = student.request_major_change(major=to_major, reason=reason, when=when)
                as_str = mesg.time_sent.strftime('%m/%d/%Y, %H:%M:%S')
                print(f'Change: {as_str} {student} to {to_major} (sent to {mesg.recipient})')

            # drop yo class
            if random() < 0.2:
                when = rand_between(aSemester.date_started, aSemester.date_ended)
                sectstuds = student.sectionstudent_set.filter(section__semester=aSemester).all()
                aSect = choice(sectstuds)
                reason = get_sentence()
                mesg = student.request_drop(sectionstudent=aSect, reason=reason, when=when)
                as_str = mesg.time_sent.strftime('%m/%d/%Y, %H:%M:%S')
                print(
                    f'DropReq: {as_str} {student} requests drop of {aSect.section} ' +
                    f'(semester {aSemester}, sent to {mesg.recipient})'
                )

            # yo be on AP
            if random() < 0.2:
                anAdmin = choice(admin_profiles)
                when = rand_between(aSemester.date_started, aSemester.date_ended)
                reason = get_sentence()
                mesg = student.notify_probation(sender=anAdmin, body=reason, when=when)
                as_str = mesg.time_sent.strftime('%m/%d/%Y, %H:%M:%S')
                print(f'AP: {as_str} {student} is on AP (sent from {mesg.sender})')

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_message')


if __name__ == "__main__":
    createData()
