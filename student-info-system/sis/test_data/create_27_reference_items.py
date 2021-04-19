import os
import sys
from random import randrange, choice, shuffle, random

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from loremipsum import Generator
from english_words import english_words_set

from sis.models import Course, Major, Professor, ReferenceItem
from django.db import connection

loremgen = Generator(dictionary=english_words_set)


def get_sentence():
    (w, s, text) = loremgen.generate_sentence()
    return text


def get_paragraph():
    (w, s, text) = loremgen.generate_paragraph()
    return text


prof_fraction = 0.75

prof_max = 5


def createData():
    error_count = 0
    profs = list(Professor.objects.all())
    shuffle(profs)
    num_profs = int(prof_fraction * len(profs))

    for prof in profs[0:num_profs]:
        major_courses = list(Course.objects.filter(major=prof.major))
        shuffle(major_courses)
        if len(major_courses) == 0:
            continue

        # do at least one course
        num_to_ref = int(0.75 * len(major_courses))
        if num_to_ref == 0:
            num_to_ref = 1

        for course in major_courses[0:num_to_ref]:
            for ix in range(1, randrange(1, prof_max)):
                aType = choice(ReferenceItem.TYPES)
                ri = ReferenceItem(
                    course=course,
                    professor=prof,
                    title=f'{get_sentence()} #{ix} for {aType[1]}',
                    type=aType[0],
                )
                if random() < .3:
                    ri.link = choice([
                        'https://www.google.com', 'https://www.amazon.com',
                        'https://www.facebook.com', 'https://www.sony.com'
                    ])
                if random() < .3:
                    ri.edition = choice(['any', 'first', 'new', 'special', 'worst'])
                if random() < .3:
                    ri.description = f'{get_sentence()}'
                try:
                    ri.save()
                except Exception:
                    error_count = error_count + 1
                    print(f'ERROR: Unable to create sec {prof} {course} {aType[1]} {ix}')
                else:
                    print(f'Created item prof {prof} {course} {aType[1]} {ix}')

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sis_referenceitem')


if __name__ == "__main__":
    createData()
