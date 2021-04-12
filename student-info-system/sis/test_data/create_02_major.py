import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from sis.models import Major, Semester, Profile
from django.db import connection
from random import sample, choice
from django.db.models import Q

specs = (
    ('GA', 'General Agriculture', 'Agriculture & Natural Resources'),
    ('APAM', 'Agriculture Production And Management', 'Agriculture & Natural Resources'),
    ('AE', 'Agricultural Economics', 'Agriculture & Natural Resources'),
    ('AS', 'Animal Sciences', 'Agriculture & Natural Resources'),
    ('FS', 'Food Science', 'Agriculture & Natural Resources'),
    ('PSAA', 'Plant Science And Agronomy', 'Agriculture & Natural Resources'),
    ('SS', 'Soil Science', 'Agriculture & Natural Resources'),
    ('MA', 'Miscellaneous Agriculture', 'Agriculture & Natural Resources'),
    ('FORE', 'Forestry', 'Agriculture & Natural Resources'),
    ('NRM', 'Natural Resources Management', 'Agriculture & Natural Resources'),
    (Semester.FALL, 'Fine Arts', 'Arts'),
    ('DATA', 'Drama And Theater Arts', 'Arts'),
    ('MUSI', 'Music', 'Arts'),
    ('VAPA', 'Visual And Performing Arts', 'Arts'),
    ('CAAGD', 'Commercial Art And Graphic Design', 'Arts'),
    ('FVAPA', 'Film Video And Photographic Arts', 'Arts'),
    ('SA', 'Studio Arts', 'Arts'),
    ('MFA', 'Miscellaneous Fine Arts', 'Arts'),
    ('ES', 'Environmental Science', 'Biology & Life Science'),
    ('BIOL', 'Biology', 'Biology & Life Science'),
    ('BS', 'Biochemical Sciences', 'Biology & Life Science'),
    ('BOTA', 'Botany', 'Biology & Life Science'),
    ('MB', 'Molecular Biology', 'Biology & Life Science'),
    ('ECOL', 'Ecology', 'Biology & Life Science'),
    ('GENE', 'Genetics', 'Biology & Life Science'),
    ('MICR', 'Microbiology', 'Biology & Life Science'),
    ('PHAR', 'Pharmacology', 'Biology & Life Science'),
    ('PHYS', 'Physiology', 'Biology & Life Science'),
    ('ZOOL', 'Zoology', 'Biology & Life Science'),
    ('NEUR', 'Neuroscience', 'Biology & Life Science'),
    ('MBN', 'Miscellaneous Biology', 'Biology & Life Science'),
    ('CSAB', 'Cognitive Science And Biopsychology', 'Biology & Life Science'),
    ('GB', 'General Business', 'Business'),
    ('ACCO', 'Accounting', 'Business'),
    ('ASZ', 'Actuarial Science', 'Business'),
    ('BMAA', 'Business Management And Administration', 'Business'),
    ('OLAE', 'Operations Logistics And E-commerce', 'Business'),
    ('BE', 'Business Economics', 'Business'),
    ('MAMR', 'Marketing And Marketing Research', 'Business'),
    ('FINA', 'Finance', 'Business'),
    ('HRAPM', 'Human Resources And Personnel Management', 'Business'),
    ('IB', 'International Business', 'Business'),
    ('HM', 'Hospitality Management', 'Business'),
    ('MISAS', 'Management Information Systems And Statistics', 'Business'),
    ('MBMA', 'Miscellaneous Business & Medical Administration', 'Business'),
    ('COMM', 'Communications', 'Communications & Journalism'),
    ('JOUR', 'Journalism', 'Communications & Journalism'),
    ('MM', 'Mass Media', 'Communications & Journalism'),
    ('AAPR', 'Advertising And Public Relations', 'Communications & Journalism'),
    ('CT', 'Communication Technologies', 'Computers & Mathematics'),
    ('CAIS', 'Computer And Information Systems', 'Computers & Mathematics'),
    ('CPADP', 'Computer Programming And Data Processing', 'Computers & Mathematics'),
    ('CS', 'Computer Science', 'Computers & Mathematics'),
    ('IS', 'Information Sciences', 'Computers & Mathematics'),
    ('CAMAS', 'Computer Administration Management And Security', 'Computers & Mathematics'),
    ('CNAT', 'Computer Networking And Telecommunications', 'Computers & Mathematics'),
    ('MATH', 'Mathematics', 'Computers & Mathematics'),
    ('AM', 'Applied Mathematics', 'Computers & Mathematics'),
    ('SADS', 'Statistics And Decision Science', 'Computers & Mathematics'),
    ('MACS', 'Mathematics And Computer Science', 'Computers & Mathematics'),
    ('GE', 'General Education', 'Education'),
    ('EAAS', 'Educational Administration And Supervision', 'Education'),
    ('SSC', 'School Student Counseling', 'Education'),
    ('EE', 'Elementary Education', 'Education'),
    ('MTE', 'Mathematics Teacher Education', 'Education'),
    ('PAHET', 'Physical And Health Education Teaching', 'Education'),
    ('ECE', 'Early Childhood Education', 'Education'),
    ('SACTE', 'Science And Computer Teacher Education', 'Education'),
    ('STE', 'Secondary Teacher Education', 'Education'),
    ('SNE', 'Special Needs Education', 'Education'),
    ('SSOHTE', 'Social Science Or History Teacher Education', 'Education'),
    ('TEML', 'Teacher Education: Multiple Levels', 'Education'),
    ('LADE', 'Language And Drama Education', 'Education'),
    ('AAME', 'Art And Music Education', 'Education'),
    ('ME', 'Miscellaneous Education', 'Education'),
    ('LS', 'Library Science', 'Education'),
    ('ARCH', 'Architecture', 'Engineering'),
    ('GEI', 'General Engineering', 'Engineering'),
    ('AET', 'Aerospace Engineering', 'Engineering'),
    ('BEB', 'Biological Engineering', 'Engineering'),
    ('AEX', 'Architectural Engineering', 'Engineering'),
    ('BEG', 'Biomedical Engineering', 'Engineering'),
    ('CE', 'Chemical Engineering', 'Engineering'),
    ('CEX', 'Civil Engineering', 'Engineering'),
    ('CEY', 'Computer Engineering', 'Engineering'),
    ('EEW', 'Electrical Engineering', 'Engineering'),
    ('EMPAS', 'Engineering Mechanics Physics And Science', 'Engineering'),
    ('EER', 'Environmental Engineering', 'Engineering'),
    ('GAGE', 'Geological And Geophysical Engineering', 'Engineering'),
    ('IAME', 'Industrial And Manufacturing Engineering', 'Engineering'),
    ('MEAMS', 'Materials Engineering And Materials Science', 'Engineering'),
    ('MEU', 'Mechanical Engineering', 'Engineering'),
    ('MEX', 'Metallurgical Engineering', 'Engineering'),
    ('MAME', 'Mining And Mineral Engineering', 'Engineering'),
    ('NAAME', 'Naval Architecture And Marine Engineering', 'Engineering'),
    ('NE', 'Nuclear Engineering', 'Engineering'),
    ('PE', 'Petroleum Engineering', 'Engineering'),
    ('MEZ', 'Miscellaneous Engineering', 'Engineering'),
    ('ET', 'Engineering Technologies', 'Engineering'),
    ('EAIM', 'Engineering And Industrial Management', 'Engineering'),
    ('EET', 'Electrical Engineering Technology', 'Engineering'),
    ('IPT', 'Industrial Production Technologies', 'Engineering'),
    ('MERT', 'Mechanical Engineering Related Technologies', 'Engineering'),
    ('MET', 'Miscellaneous Engineering Technologies', 'Engineering'),
    ('MS', 'Materials Science', 'Engineering'),
    ('NS', 'Nutrition Sciences', 'Health'),
    ('GMAHS', 'General Medical And Health Services', 'Health'),
    ('CDSAS', 'Communication Disorders Sciences And Services', 'Health'),
    ('HAMAS', 'Health And Medical Administrative Services', 'Health'),
    ('MAS', 'Medical Assisting Services', 'Health'),
    ('MTT', 'Medical Technologies Technicians', 'Health'),
    ('HAMPP', 'Health And Medical Preparatory Programs', 'Health'),
    ('NURS', 'Nursing', 'Health'),
    ('PPSAA', 'Pharmacy Pharmaceutical Sciences And Administration', 'Health'),
    ('TTP', 'Treatment Therapy Professions', 'Health'),
    ('CAPH', 'Community And Public Health', 'Health'),
    ('MHMP', 'Miscellaneous Health Medical Professions', 'Health'),
    ('AEACS', 'Area Ethnic And Civilization Studies', 'Humanities & Liberal Arts'),
    ('LACLAL', 'Linguistics And Comparative Language And Literature',
     'Humanities & Liberal Arts'),
    ('FGLAOCFLS', 'French German Latin And Other Common Foreign Language Studies',
     'Humanities & Liberal Arts'),
    ('OFL', 'Other Foreign Languages', 'Humanities & Liberal Arts'),
    ('ELAL', 'English Language And Literature', 'Humanities & Liberal Arts'),
    ('CAR', 'Composition And Rhetoric', 'Humanities & Liberal Arts'),
    ('LA', 'Liberal Arts', 'Humanities & Liberal Arts'),
    ('HUMA', 'Humanities', 'Humanities & Liberal Arts'),
    ('IAIS', 'Intercultural And International Studies', 'Humanities & Liberal Arts'),
    ('PARS', 'Philosophy And Religious Studies', 'Humanities & Liberal Arts'),
    ('TARV', 'Theology And Religious Vocations', 'Humanities & Liberal Arts'),
    ('AAA', 'Anthropology And Archeology', 'Humanities & Liberal Arts'),
    ('AHAC', 'Art History And Criticism', 'Humanities & Liberal Arts'),
    ('HIST', 'History', 'Humanities & Liberal Arts'),
    ('USH', 'United States History', 'Humanities & Liberal Arts'),
    ('CSACA', 'Cosmetology Services And Culinary Arts', 'Industrial Arts & Consumer Services'),
    ('FACS', 'Family And Consumer Sciences', 'Industrial Arts & Consumer Services'),
    ('MT', 'Military Technologies', 'Industrial Arts & Consumer Services'),
    ('PFPRAL', 'Physical Fitness Parks Recreation And Leisure',
     'Industrial Arts & Consumer Services'),
    ('CSP', 'Construction Services', 'Industrial Arts & Consumer Services'),
    ('', '"electrical', ' Mechanical'),
    ('TSAT', 'Transportation Sciences And Technologies', 'Industrial Arts & Consumer Services'),
    ('MSQ', 'Multi/interdisciplinary Studies', 'Interdisciplinary'),
    ('CR', 'Court Reporting', 'Law & Public Policy'),
    ('PALS', 'Pre-law And Legal Studies', 'Law & Public Policy'),
    ('CJAFP', 'Criminal Justice And Fire Protection', 'Law & Public Policy'),
    ('PA', 'Public Administration', 'Law & Public Policy'),
    ('PP', 'Public Policy', 'Law & Public Policy'),
    ('PS', 'Physical Sciences', 'Physical Sciences'),
    ('AAAY', 'Astronomy And Astrophysics', 'Physical Sciences'),
    ('ASAM', 'Atmospheric Sciences And Meteorology', 'Physical Sciences'),
    ('CHEM', 'Chemistry', 'Physical Sciences'),
    ('GAES', 'Geology And Earth Science', 'Physical Sciences'),
    ('GEOS', 'Geosciences', 'Physical Sciences'),
    ('OCEA', 'Oceanography', 'Physical Sciences'),
    ('PHYSY', 'Physics', 'Physical Sciences'),
    ('MOGS', 'Multi-disciplinary Or General Science', 'Physical Sciences'),
    ('W', '"nuclear', ' Industrial Radiology'),
    ('PSYC', 'Psychology', 'Psychology & Social Work'),
    ('EP', 'Educational Psychology', 'Psychology & Social Work'),
    ('CP', 'Clinical Psychology', 'Psychology & Social Work'),
    ('CPM', 'Counseling Psychology', 'Psychology & Social Work'),
    ('IAOP', 'Industrial And Organizational Psychology', 'Psychology & Social Work'),
    ('SP', 'Social Psychology', 'Psychology & Social Work'),
    ('MP', 'Miscellaneous Psychology', 'Psychology & Social Work'),
    ('HSACO', 'Human Services And Community Organization', 'Psychology & Social Work'),
    ('SW', 'Social Work', 'Psychology & Social Work'),
    ('ISS', 'Interdisciplinary Social Sciences', 'Social Science'),
    ('GSS', 'General Social Sciences', 'Social Science'),
    ('ECON', 'Economics', 'Social Science'),
    ('CRIM', 'Criminology', 'Social Science'),
    ('GEOG', 'Geography', 'Social Science'),
    ('IR', 'International Relations', 'Social Science'),
    ('PSAG', 'Political Science And Government', 'Social Science'),
    ('SOCI', 'Sociology', 'Social Science'),
    ('MSS', 'Miscellaneous Social Sciences', 'Social Science'),
)


def createData():
    to_generate = 25

    admins = list(
        Profile.objects.filter(Q(role=Profile.ACCESS_ADMIN) | Q(role=Profile.ACCESS_PROFESSOR)))
    error_count = 0

    for (a, t, d) in sample(specs, k=to_generate):
        anAdmin = choice(admins)
        m = Major(abbreviation=a, title=t, description=d, contact=anAdmin)
        try:
            m.save()
        except Exception:
            print(f'ERROR: Unable to save major {a} {t} (contact: ' + f'{anAdmin.user.username})')
            error_count = error_count + 1
        else:
            print(f'create major {a} {t} {d} (contact: {anAdmin.user.username})')

    if error_count:
        print(f'ERROR: {error_count} errors occurred')


def cleanData():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sis_major")


if __name__ == "__main__":
    createData()
