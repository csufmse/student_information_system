from django.test import TestCase
from datetime import datetime

from django.contrib.auth.models import User

from sis.models import (Course, CoursePrerequisite, Major, Professor, Section, SectionStudent,
                        Semester, Student, TranscriptRequest, AccessRoles, ClassLevel)

from sis.tests.utils import (createAdmin, createStudent, createProfessor, createCourse)


class StudentTestCase_Basic(TestCase):

    @classmethod
    def setUpTestData(cls):
        m = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        StudentTestCase_Basic.major = m

        StudentTestCase_Basic.stud = createStudent(major=m, username='testUser')

        StudentTestCase_Basic.c1 = Course.objects.create(major=m,
                                                         catalog_number='101',
                                                         title="required by major",
                                                         credits_earned=3.0)
        StudentTestCase_Basic.c2 = Course.objects.create(major=m,
                                                         catalog_number='102',
                                                         title="required by major",
                                                         credits_earned=3.0)

        StudentTestCase_Basic.semester = Semester.objects.create(
            date_registration_opens=datetime.now(),
            date_started=datetime.now(),
            date_last_drop=datetime.now(),
            date_ended=datetime.now(),
            semester=Semester.FALL,
            year=2000)

    def test_class_level(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.class_level(), 'Freshman')

    def test_gpa(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.gpa(), 0.0)

    def test_credits_earned(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.credits_earned(), 0)

    def test_major(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.major, StudentTestCase_Basic.major)

    def test_name(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.name, 't estUser')

    def test_semesters(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.semesters.count(), 0)

    def test_sections(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.sectionstudent_set.count(), 0)

    def test_history(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.course_history().count(), 0)

    def test_remaining_required(self):
        student = StudentTestCase_Basic.stud
        self.assertEqual(student.remaining_required_courses().count(), 0)


class StudentTestCase_History(TestCase):

    @classmethod
    def setUpTestData(cls):
        m = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        StudentTestCase_History.major = m

        StudentTestCase_History.stud = createStudent(major=m, username='testUser')
        p = createProfessor(major=m, username='tprof1')

        m_eng = Major.objects.create(abbreviation="ENGL", name="English")

        StudentTestCase_History.c1 = Course.objects.create(major=m,
                                                           catalog_number='101',
                                                           title="required by major",
                                                           credits_earned=3.0)
        StudentTestCase_History.c2 = Course.objects.create(major=m,
                                                           catalog_number='102',
                                                           title="required by major",
                                                           credits_earned=2.0)
        StudentTestCase_History.c3 = Course.objects.create(major=m,
                                                           catalog_number='103',
                                                           title="required by major",
                                                           credits_earned=6.0)
        StudentTestCase_History.c4 = Course.objects.create(major=m,
                                                           catalog_number='104',
                                                           title="not required by major",
                                                           credits_earned=2.0)
        StudentTestCase_History.e1 = Course.objects.create(major=m_eng,
                                                           catalog_number='218',
                                                           title="required by CPSC 104",
                                                           credits_earned=3.0)
        StudentTestCase_History.e2 = Course.objects.create(major=m_eng,
                                                           catalog_number='300',
                                                           title="required by CPSC 102",
                                                           credits_earned=3.0)

        # set up required by major
        m.courses_required.add(StudentTestCase_History.c1, StudentTestCase_History.c2,
                               StudentTestCase_History.c3)
        m.save()

        # set up course prereqs
        CoursePrerequisite.objects.create(course=StudentTestCase_History.c2,
                                          prerequisite=StudentTestCase_History.e2)
        CoursePrerequisite.objects.create(course=StudentTestCase_History.c4,
                                          prerequisite=StudentTestCase_History.e1)

        StudentTestCase_History.semester = Semester.objects.create(
            date_registration_opens=datetime.now(),
            date_started=datetime.now(),
            date_last_drop=datetime.now(),
            date_ended=datetime.now(),
            semester=Semester.FALL,
            year=2000)

        StudentTestCase_History.stud.semesters.add(StudentTestCase_History.semester)
        StudentTestCase_History.stud.save()

        StudentTestCase_History.sec1 = Section.objects.create(
            course=StudentTestCase_History.c1,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.sec2 = Section.objects.create(
            course=StudentTestCase_History.c2,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.sec3 = Section.objects.create(
            course=StudentTestCase_History.c3,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.sec4 = Section.objects.create(
            course=StudentTestCase_History.e2,
            semester=StudentTestCase_History.semester,
            professor=p)
        StudentTestCase_History.studsec1 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec1,
            student=StudentTestCase_History.stud,
            status=SectionStudent.GRADED,
            grade=SectionStudent.GRADE_B)
        StudentTestCase_History.studsec2 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec2,
            student=StudentTestCase_History.stud,
            status=SectionStudent.GRADED,
            grade=SectionStudent.GRADE_F)
        StudentTestCase_History.studsec3 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec3,
            student=StudentTestCase_History.stud,
            status=SectionStudent.DROPPED)
        StudentTestCase_History.studsec4 = SectionStudent.objects.create(
            section=StudentTestCase_History.sec4,
            student=StudentTestCase_History.stud,
            status=SectionStudent.GRADED,
            grade=SectionStudent.GRADE_C)
        # c1: required, passed (B)
        # c2: required, failed
        # c3: required, (DROPPED)
        # c4: not required, not taken
        # e1: a prereq of c4
        # e2: a prereq of c2

    def test_gpa(self):
        student = (User.objects.get(username="testUser")).student
        self.assertEqual(student.gpa(), (3 * 3.0 + 0 * 2.0 + 2 * 3.0) / (3.0 + 2.0 + 3.0))

    def test_semesters(self):
        student = StudentTestCase_History.stud
        self.assertEqual(student.semesters.count(), 1)

    def test_history_all(self):
        student = StudentTestCase_History.stud
        history = student.course_history()
        self.assertEqual(history.count(), 4)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec2)
        self.assertEqual(history[2].section, StudentTestCase_History.sec3)
        self.assertEqual(history[3].section, StudentTestCase_History.sec4)

    def test_history_passed(self):
        student = StudentTestCase_History.stud
        history = student.course_history(passed=True)
        self.assertEqual(history.count(), 2)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec4)

    def test_history_graded(self):
        student = StudentTestCase_History.stud
        history = student.course_history(graded=True)
        self.assertEqual(history.count(), 3)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec2)
        self.assertEqual(history[2].section, StudentTestCase_History.sec4)

    def test_history_required(self):
        student = StudentTestCase_History.stud
        history = student.course_history(required=True)
        self.assertEqual(history.count(), 3)
        self.assertEqual(history[0].section, StudentTestCase_History.sec1)
        self.assertEqual(history[1].section, StudentTestCase_History.sec2)
        self.assertEqual(history[2].section, StudentTestCase_History.sec3)

    def test_history_prereqs_not_fulfilled(self):
        student = StudentTestCase_History.stud
        history = student.course_history(prereqs_for=StudentTestCase_History.c4)
        self.assertEqual(history.count(), 0)

    def test_history_prereqs_fulfilled(self):
        student = StudentTestCase_History.stud
        history = student.course_history(prereqs_for=StudentTestCase_History.c2)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history[0].section, StudentTestCase_History.sec4)

    def test_credits_earned(self):
        student = StudentTestCase_History.stud
        self.assertEqual(student.credits_earned(), 3.0 + 3.0)

    def test_remaining_required(self):
        student = StudentTestCase_History.stud
        rem = student.remaining_required_courses()
        self.assertEqual(rem.count(), 2)
        self.assertEqual(rem[0], StudentTestCase_History.c2)
        self.assertEqual(rem[1], StudentTestCase_History.c3)


class ProfessorTestCase(TestCase):

    def setUp(self):
        User.objects.create(username="prof", first_name="First", last_name="Last")

    def test_professor_name(self):
        user = User.objects.get(username="prof")
        professor = Professor.objects.create(user=user)
        self.assertEqual(professor.name, "First Last")


class Professor_teaching_test(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(Professor_teaching_test, cls).setUpTestData()
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")

        Professor_teaching_test.professor = createProfessor(major, "test")

        Professor_teaching_test.course = Course.objects.create(major=major,
                                                               catalog_number='101',
                                                               title="Intro To Test",
                                                               credits_earned=3.0)

        Professor_teaching_test.semester = Semester.objects.create(
            date_registration_opens=datetime.now(),
            date_started=datetime.now(),
            date_last_drop=datetime.now(),
            date_ended=datetime.now(),
            semester=Semester.FALL,
            year=2000)

    def test_no_teaching(self):
        self.assertEqual(Professor_teaching_test.professor.semesters_teaching().count(), 0)

    def test_teaching(self):
        s = Section.objects.create(course=Professor_teaching_test.course,
                                   professor=Professor_teaching_test.professor,
                                   semester=Professor_teaching_test.semester,
                                   number=1,
                                   hours="MW 1200-1400")
        teaching_sems = Professor_teaching_test.professor.semesters_teaching()
        self.assertEqual(teaching_sems.count(), 1)
        self.assertEqual(str(teaching_sems[0]), "FA-2000")
        s.delete()


class CourseTestCase_Basic(TestCase):

    def setUp(self):
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        Course.objects.create(major=major,
                              catalog_number='101',
                              title="Intro To Test",
                              credits_earned=3.0)

    def test_course_major_name(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.major_name, "Computer Science")

    def test_course_name(self):
        course = Course.objects.get(title="Intro To Test")
        self.assertEqual(course.name, "CPSC-101")


class CourseTestCase_deps(TestCase):

    @classmethod
    def setUpTestData(cls):
        m = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        CourseTestCase_deps.major = m

        CourseTestCase_deps.courses = {}
        for i in range(1, 15):
            CourseTestCase_deps.courses[i] = createCourse(m, str(i))

    def test_none(self):
        cs = CourseTestCase_deps.courses
        self.assertEqual(cs[1].are_candidate_prerequisites_valid(), True)

    def test_valid_candidate(self):
        cs = CourseTestCase_deps.courses
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2]]), True)

    def test_candidate_loop(self):
        cs = CourseTestCase_deps.courses
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[1]]), False)

    def test_candidate_chain(self):
        cs = CourseTestCase_deps.courses
        cp = CoursePrerequisite.objects.create(course=cs[2], prerequisite=cs[3])
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2]]), True)
        cp.delete()

    def test_candidate_loop(self):
        cs = CourseTestCase_deps.courses
        cp1 = CoursePrerequisite.objects.create(course=cs[2], prerequisite=cs[3])
        cp2 = CoursePrerequisite.objects.create(course=cs[3], prerequisite=cs[1])
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2]]), False)
        cp1.delete()
        cp2.delete()

    def test_double_dep(self):
        cs = CourseTestCase_deps.courses
        cp1 = CoursePrerequisite.objects.create(course=cs[2], prerequisite=cs[3])
        cp2 = CoursePrerequisite.objects.create(course=cs[5], prerequisite=cs[3])
        self.assertEqual(cs[1].are_candidate_prerequisites_valid([cs[2], cs[5]]), True)
        cp1.delete()
        cp2.delete()

    def test_offset(self):
        cs = CourseTestCase_deps.courses

        def cp(c, p):
            return CoursePrerequisite.objects.create(course=cs[c], prerequisite=cs[p])

        cp(1, 11)
        cp(11, 5)
        cp(1, 5)
        cp(5, 6)
        cp(6, 7)
        self.assertEqual(cs[1].are_candidate_prerequisites_valid(), True)


class CourseMeetingPrereqsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        KLASS = CourseMeetingPrereqsTest
        super(KLASS, cls).setUpTestData()
        KLASS.m1 = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        KLASS.c1 = Course.objects.create(major=KLASS.m1,
                                         catalog_number='300',
                                         title="Intro To Test",
                                         credits_earned=3.0)
        KLASS.c2 = Course.objects.create(major=KLASS.m1,
                                         catalog_number='400',
                                         title="Outro To Test",
                                         credits_earned=3.0)
        CoursePrerequisite.objects.create(course=KLASS.c2, prerequisite=KLASS.c1)
        KLASS.sem = Semester.objects.create(date_registration_opens=datetime.now(),
                                            date_started=datetime.now(),
                                            date_last_drop=datetime.now(),
                                            date_ended=datetime.now(),
                                            semester=Semester.FALL,
                                            year=2000)
        p = createProfessor(username='frodo', major=KLASS.m1)
        KLASS.sec1 = Section.objects.create(course=KLASS.c1,
                                            professor=p,
                                            semester=KLASS.sem,
                                            number=1,
                                            hours="MW 1200-1400")
        KLASS.stud = createStudent(username='tester', major=KLASS.m1)

    def test_courseprereqs_none(self):
        KLASS = CourseMeetingPrereqsTest
        self.assertEqual(len(KLASS.c1.prerequisites_met_list(student=KLASS.stud)), 0)

    def test_courseprereqs_notmet(self):
        KLASS = CourseMeetingPrereqsTest
        pr = KLASS.c2.prerequisites_met_list(student=KLASS.stud)
        self.assertEqual(len(pr), 1)
        self.assertEqual(pr[0].name, KLASS.c1.name)
        self.assertFalse(pr[0].met)

    def test_courseprereqs_not_met_failed(self):
        KLASS = CourseMeetingPrereqsTest
        secstud = SectionStudent.objects.create(section=KLASS.sec1, student=KLASS.stud)
        secstud.status = SectionStudent.GRADED
        secstud.grade = SectionStudent.GRADE_F
        secstud.save()
        pr = KLASS.c2.prerequisites_met_list(student=KLASS.stud)
        self.assertEqual(len(pr), 1)
        self.assertEqual(pr[0].name, KLASS.c1.name)
        self.assertFalse(pr[0].met)
        secstud.delete()

    def test_courseprereqs_met(self):
        KLASS = CourseMeetingPrereqsTest
        secstud = SectionStudent.objects.create(section=KLASS.sec1, student=KLASS.stud)
        secstud.status = SectionStudent.GRADED
        secstud.grade = SectionStudent.GRADE_A
        secstud.save()
        pr = KLASS.c2.prerequisites_met_list(student=KLASS.stud)
        self.assertEqual(len(pr), 1)
        self.assertEqual(pr[0].name, KLASS.c1.name)
        self.assertTrue(pr[0].met)
        secstud.delete()


class SectionTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(SectionTestCase, cls).setUpTestData()
        user = User.objects.create(username="prof", first_name="First", last_name="Last")
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        professor = Professor.objects.create(user=user)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester=Semester.FALL,
                                           year=2000)
        Section.objects.create(course=course,
                               professor=professor,
                               semester=semester,
                               number=1,
                               hours="MW 1200-1400")

    def test_section_course_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.course_name, "CPSC-101")

    def test_section_professor_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.professor_name, "First Last")

    def test_section_semester_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.semester_name, "FA-2000")

    def test_section_name(self):
        section = Section.objects.get(hours="MW 1200-1400")
        self.assertEqual(section.name, "CPSC-101-1")


class MajorTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(MajorTestCase, cls).setUpTestData()
        MajorTestCase.m1 = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        MajorTestCase.c1 = Course.objects.create(major=MajorTestCase.m1,
                                                 catalog_number='400',
                                                 title="ZZZ Intro To Test",
                                                 credits_earned=3.0)
        MajorTestCase.c2 = Course.objects.create(major=MajorTestCase.m1,
                                                 catalog_number='300',
                                                 title="AAA More Test",
                                                 credits_earned=3.0)
        MajorTestCase.c3 = Course.objects.create(major=MajorTestCase.m1,
                                                 catalog_number='350',
                                                 title="PPP Still More",
                                                 credits_earned=3.0)
        MajorTestCase.m1.courses_required.add(MajorTestCase.c1)
        MajorTestCase.m1.courses_required.add(MajorTestCase.c2)
        MajorTestCase.m1.courses_required.add(MajorTestCase.c3)
        MajorTestCase.m1.save()

    def test_major_abbrev(self):
        m = Major.objects.get(name='Computer Science')
        self.assertEqual(m.abbreviation, "CPSC")

    def test_major_name(self):
        m = Major.objects.get(abbreviation='CPSC')
        self.assertEqual(m.name, "Computer Science")

    def test_required_order(self):
        m = Major.objects.get(abbreviation='CPSC')
        self.assertEqual(m.courses_required.count(), 3)
        self.assertEqual(m.courses_required.all()[0].catalog_number, '300')
        self.assertEqual(m.courses_required.all()[1].catalog_number, '350')
        self.assertEqual(m.courses_required.all()[2].catalog_number, '400')

    def test_requirements_met_none(self):
        m1 = MajorTestCase.m1
        s = createStudent(username='frodo', major=m1)
        reql = m1.requirements_met_list(s)
        self.assertEqual(len(reql), 3)
        for c in reql:
            self.assertFalse(c.met)
        s.delete()

    def test_requirements_met_some(self):
        m1 = MajorTestCase.m1
        p = createProfessor(major=m1, username='herc')
        s = createStudent(username='frodo', major=m1)

        sem = Semester.objects.create(date_registration_opens=datetime.now(),
                                      date_started=datetime.now(),
                                      date_last_drop=datetime.now(),
                                      date_ended=datetime.now(),
                                      semester=Semester.FALL,
                                      year=2000)
        sec1 = Section.objects.create(course=MajorTestCase.c1, semester=sem, professor=p)

        sec1stud = SectionStudent.objects.create(section=sec1, student=s, status='REGISTERED')

        # has not completed
        reql = m1.requirements_met_list(s)
        self.assertEqual(len(reql), 3)
        for c in reql:
            self.assertFalse(c.met)

        # failed
        sec1stud.status = 'Graded'
        sec1stud.grade = 0.0
        sec1stud.save()

        reql = m1.requirements_met_list(s)
        self.assertEqual(len(reql), 3)
        for c in reql:
            self.assertFalse(c.met)

        # passing
        sec1stud.grade = 3.0
        sec1stud.save()

        reql = m1.requirements_met_list(s)
        self.assertEqual(len(reql), 3)
        for c in reql:
            if c.met:
                self.assertEqual(c.catalog_number, '400')
            else:
                self.assertNotEqual(c.catalog_number, '400')


class ClassLevel_tests(TestCase):

    def test_null_credits(self):
        self.assertEqual(ClassLevel.level(None), ClassLevel.FRESHMAN)

    def test_nega_credits(self):
        self.assertEqual(ClassLevel.level(-34), ClassLevel.FRESHMAN)

    def test_freshman(self):
        self.assertEqual(ClassLevel.level(10), ClassLevel.FRESHMAN)

    def test_sophomore(self):
        self.assertEqual(ClassLevel.level(40), ClassLevel.SOPHOMORE)

    def test_junior(self):
        self.assertEqual(ClassLevel.level(68), ClassLevel.JUNIOR)

    def test_senior(self):
        self.assertEqual(ClassLevel.level(98), ClassLevel.SENIOR)


class Semester_tests(TestCase):

    def test_names(self):
        self.assertEqual(Semester.name_for_session(Semester.FALL), 'Fall')
        self.assertEqual(Semester.name_for_session(Semester.SPRING), 'Spring')
        self.assertEqual(Semester.name_for_session(Semester.SUMMER), 'Summer')
        self.assertEqual(Semester.name_for_session(Semester.WINTER), 'Winter')

    def test_bad_name(self):
        self.assertRaises(Exception, Semester.name_for_session('xx'))

    def test_order_fields(self):
        s1 = Semester.objects.create(date_registration_opens=datetime.now(),
                                     date_started=datetime.now(),
                                     date_last_drop=datetime.now(),
                                     date_ended=datetime.now(),
                                     semester=Semester.FALL,
                                     year=2000)
        # forcing the fetch here lets the annotation generate the extra attributes
        s2 = Semester.objects.get(year=2000)

        self.assertEqual(s2.session_name, 'Fall')
        self.assertEqual(s2.semester_order, '2000-0')
        self.assertEqual(s2.session_order, 0)


class SemesterProf_tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        KLASS = SemesterProf_tests
        super(SemesterProf_tests, cls).setUpTestData()
        KLASS.sem = Semester.objects.create(date_registration_opens=datetime.now(),
                                            date_started=datetime.now(),
                                            date_last_drop=datetime.now(),
                                            date_ended=datetime.now(),
                                            semester=Semester.FALL,
                                            year=2000)

        KLASS.m1 = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        KLASS.p1 = createProfessor(username='frodo', major=KLASS.m1)
        KLASS.p2 = createProfessor(username='bilbo', major=KLASS.m1)
        KLASS.courses = []
        for num in range(100, 120, 2):
            KLASS.courses.append(createCourse(major=KLASS.m1, num=num))

    def test_professors_none(self):
        KLASS = SemesterProf_tests
        self.assertEqual(len(KLASS.sem.professors_teaching()), 0)

    def test_professors_uno(self):
        KLASS = SemesterProf_tests
        s1 = Section.objects.create(course=KLASS.courses[0],
                                    professor=KLASS.p1,
                                    semester=KLASS.sem,
                                    number=1,
                                    hours="MW 1200-1400")
        self.assertEqual(len(KLASS.sem.professors_teaching()), 1)
        s1.delete()

    def test_professors_still_uno(self):
        KLASS = SemesterProf_tests
        s1 = Section.objects.create(course=KLASS.courses[0],
                                    professor=KLASS.p1,
                                    semester=KLASS.sem,
                                    number=1,
                                    hours="MW 1200-1400")
        s2 = Section.objects.create(course=KLASS.courses[1],
                                    professor=KLASS.p1,
                                    semester=KLASS.sem,
                                    number=1,
                                    hours="MW 1200-1400")
        self.assertEqual(len(KLASS.sem.professors_teaching()), 1)
        s1.delete()
        s2.delete()

    def test_professors_dos(self):
        KLASS = SemesterProf_tests
        s1 = Section.objects.create(course=KLASS.courses[0],
                                    professor=KLASS.p1,
                                    semester=KLASS.sem,
                                    number=1,
                                    hours="MW 1200-1400")
        s2 = Section.objects.create(course=KLASS.courses[1],
                                    professor=KLASS.p2,
                                    semester=KLASS.sem,
                                    number=1,
                                    hours="MW 1200-1400")
        self.assertEqual(len(KLASS.sem.professors_teaching()), 2)
        s1.delete()
        s2.delete()
