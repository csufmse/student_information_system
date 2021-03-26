from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from sis.models import (Admin, Course, CoursePrerequisite, Major, Professor, Section,
                        SectionStudent, Semester, SemesterStudent, Student, TranscriptRequest,
                        UpperField)


class AdminViewsAccessTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<23fwd+tuK')
        test_user1.save()
        admin = Admin.objects.create(user=test_user1)
        admin.save()
        test_user2 = User.objects.create_user(username='testuser2', password='1X<23fwd+tuK')
        test_user2.save()
        prof = Professor.objects.create(user=test_user2)
        prof.save()
        test_user3 = User.objects.create_user(username='testuser3', password='1X<23fwd+tuK')
        test_user3.save()
        stud = Student.objects.create(user=test_user3)
        stud.save()

    # list views
    def test_home_view_exists_for_admin(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/')
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/home_admin.html')

    def test_home_view_redirects_for_prof(self):
        login = self.client.login(username='testuser2', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirects_for_stud(self):
        login = self.client.login(username='testuser3', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_redirect_login_for_loser(self):
        response = self.client.get('/schooladmin/')
        self.assertEqual(response.status_code, 302)

    def test_home_view_login_for_loser(self):
        response = self.client.get('/schooladmin/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')


class AdminUserViewsTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<23fwd+tuK')
        test_user1.save()
        admin = Admin.objects.create(user=test_user1)
        admin.save()

    # list views
    def test_users_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/users')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_user_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_user_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user/1/edit')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_new_user_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user_new')
        self.assertEqual(response.status_code, 200)

    # misc
    def test_user_pass_change_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/user/1/change_password')
        self.assertEqual(response.status_code, 200)


class AdminMajorViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(AdminMajorViewsTest, cls).setUpTestData()
        AdminMajorViewsTest.test_user1 = User.objects.create_user(username='testuser1',
                                                                  password='1X<23fwd+tuK')
        Admin.objects.create(user=AdminMajorViewsTest.test_user1)
        AdminMajorViewsTest.m1 = Major.objects.create(abbreviation="CPSC",
                                                      name="Computer Science")
        AdminMajorViewsTest.m2 = Major.objects.create(abbreviation="ENGL", name="English")
        AdminMajorViewsTest.m3 = Major.objects.create(abbreviation="LIT", name="Literature")
        AdminMajorViewsTest.c1 = Course.objects.create(major=AdminMajorViewsTest.m1,
                                                       catalog_number='101',
                                                       title="Intro To Test",
                                                       credits_earned=3.0)
        AdminMajorViewsTest.c2 = Course.objects.create(major=AdminMajorViewsTest.m1,
                                                       catalog_number='102',
                                                       title="More Test",
                                                       credits_earned=3.0)
        AdminMajorViewsTest.c3 = Course.objects.create(major=AdminMajorViewsTest.m3,
                                                       catalog_number='101',
                                                       title="something else",
                                                       credits_earned=3.0)
        AdminMajorViewsTest.m1.courses_required.add(AdminMajorViewsTest.c1)
        AdminMajorViewsTest.m1.courses_required.add(AdminMajorViewsTest.c3)
        AdminMajorViewsTest.m1.save()

    def test_majors_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/majors')
        self.assertEqual(response.status_code, 200)

    def test_majors_view_uses_template(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/majors')
        self.assertTemplateUsed(response, 'schooladmin/majors.html')

    # single-object views
    def test_major_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/major/' + AdminMajorViewsTest.m1.abbreviation)
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_major_fails_view(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/major/' + 'CRAP')
        self.assertEqual(response.status_code, 404)

    def test_major_view_uses_template(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/major/' + AdminMajorViewsTest.m1.abbreviation)
        self.assertTemplateUsed(response, 'schooladmin/major.html')

    # edit views
    def test_edit_major_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/major/' + AdminMajorViewsTest.m1.abbreviation +
                                   '/edit')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/major_edit.html')

    # create views
    def test_new_major_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/major_new')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schooladmin/major_new.html')


class AdminCoursesViewsTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<23fwd+tuK')
        test_user1.save()
        admin = Admin.objects.create(user=test_user1)
        admin.save()

    @classmethod
    def setUpTestData(self):
        user_p = User.objects.create(username="prof", first_name="First", last_name="Last")
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        professor = Professor.objects.create(user=user_p, major=major)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester='FA',
                                           year=2000)
        section = Section.objects.create(course=course,
                                         professor=professor,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        user_s = User.objects.create(username="stud", first_name="First", last_name="Last")
        self.student = Student.objects.create(user=user_s, major=major)
        self.student.sections.add(section)

    # list views
    def test_courses_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/courses')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_course_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/course/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_course_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/course/1/edit')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_new_course_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/course_new')
        self.assertEqual(response.status_code, 200)

    # misc
    def test_course_new_section_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/course/1/section_new')
        self.assertEqual(response.status_code, 200)


class AdminSectionViewsTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<23fwd+tuK')
        test_user1.save()
        admin = Admin.objects.create(user=test_user1)
        admin.save()

    @classmethod
    def setUpTestData(self):
        user_p = User.objects.create(username="prof", first_name="First", last_name="Last")
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        professor = Professor.objects.create(user=user_p, major=major)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester='FA',
                                           year=2000)
        section = Section.objects.create(course=course,
                                         professor=professor,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        user_s = User.objects.create(username="stud", first_name="First", last_name="Last")
        self.student = Student.objects.create(user=user_s, major=major)
        self.student.sections.add(section)

    # list views
    def test_sections_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/sections')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_section_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/section/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_section_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/section/1/edit')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_new_section_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/section_new')
        self.assertEqual(response.status_code, 200)


class AdminSemesterViewsTest(TestCase):

    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<23fwd+tuK')
        test_user1.save()
        admin = Admin.objects.create(user=test_user1)
        admin.save()

    @classmethod
    def setUpTestData(self):
        user_p = User.objects.create(username="prof", first_name="First", last_name="Last")
        major = Major.objects.create(abbreviation="CPSC", name="Computer Science")
        course = Course.objects.create(major=major,
                                       catalog_number='101',
                                       title="Intro To Test",
                                       credits_earned=3.0)
        professor = Professor.objects.create(user=user_p, major=major)
        semester = Semester.objects.create(date_registration_opens=datetime.now(),
                                           date_started=datetime.now(),
                                           date_last_drop=datetime.now(),
                                           date_ended=datetime.now(),
                                           semester='FA',
                                           year=2000)
        section = Section.objects.create(course=course,
                                         professor=professor,
                                         semester=semester,
                                         number=1,
                                         hours="MW 1200-1400")
        user_s = User.objects.create(username="stud", first_name="First", last_name="Last")
        self.student = Student.objects.create(user=user_s, major=major)
        self.student.sections.add(section)

    # list views
    def test_semesters_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semesters')
        self.assertEqual(response.status_code, 200)

    # single-object views
    def test_semester_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semester/1')
        self.assertEqual(response.status_code, 200)

    # edit views
    def test_edit_semesters_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semester/1/edit')
        self.assertEqual(response.status_code, 200)

    # create views
    def test_new_semesters_view_exists(self):
        login = self.client.login(username='testuser1', password='1X<23fwd+tuK')
        response = self.client.get('/schooladmin/semester_new')
        self.assertEqual(response.status_code, 200)
