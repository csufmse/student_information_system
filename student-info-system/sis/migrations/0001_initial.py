# Generated by Django 3.1.7 on 2021-04-03 07:10

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import sis.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
            ],
            options={
                'ordering': ['user__username'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalog_number', models.CharField(max_length=20, verbose_name='Number')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('description', models.CharField(blank=True, max_length=256, verbose_name='Description')),
                ('credits_earned', models.DecimalField(decimal_places=1, max_digits=2, verbose_name='Credits')),
            ],
            options={
                'ordering': ['major', 'catalog_number', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Major',
            fields=[
                ('abbreviation', sis.models.UpperField(max_length=6, primary_key=True, serialize=False, verbose_name='Abbreviation')),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=256, verbose_name='Description')),
                ('courses_required', models.ManyToManyField(blank=True, related_name='required_by', to='sis.Course')),
            ],
            options={
                'ordering': ['abbreviation'],
            },
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('major', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sis.major')),
            ],
            options={
                'ordering': ['user__username'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Section Number')),
                ('capacity', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Capacity')),
                ('hours', models.CharField(max_length=256, verbose_name='Hours')),
                ('status', models.CharField(choices=[('Closed', 'Closed'), ('Open', 'Open'), ('In Progress', 'In Progress'), ('Grading', 'Grading'), ('Graded', 'Graded'), ('Cancelled', 'Cancelled')], default='Closed', max_length=20, verbose_name='Section Status')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis.course')),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis.professor')),
            ],
            options={
                'ordering': ['semester', 'course', 'number'],
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_registration_opens', models.DateField(verbose_name='Registration Opens')),
                ('date_registration_closes', models.DateField(verbose_name='Registration Closes')),
                ('date_started', models.DateField(verbose_name='Classes Start')),
                ('date_last_drop', models.DateField(verbose_name='Last Drop')),
                ('date_ended', models.DateField(verbose_name='Classes End')),
                ('semester', models.CharField(choices=[('FA', 'Fall'), ('WI', 'Winter'), ('SP', 'Spring'), ('SU', 'Summer')], default='FA', max_length=6, verbose_name='semester')),
                ('year', models.IntegerField(default=2000, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2300)], verbose_name='year')),
            ],
            options={
                'ordering': ['date_started'],
                'unique_together': {('semester', 'year')},
            },
        ),
        migrations.CreateModel(
            name='SemesterStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis.semester')),
            ],
            options={
                'ordering': ['semester', 'student'],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('major', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sis.major')),
                ('semesters', models.ManyToManyField(related_name='semester_students', through='sis.SemesterStudent', to='sis.Semester')),
            ],
            options={
                'ordering': ['user__username'],
            },
        ),
        migrations.AddField(
            model_name='semesterstudent',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis.student'),
        ),
        migrations.CreateModel(
            name='SectionStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.SmallIntegerField(blank=True, choices=[(4, 'A'), (3, 'B'), (2, 'C'), (1, 'D'), (0, 'F')], default=None, null=True)),
                ('status', models.CharField(choices=[('Registered', 'Registered'), ('Done', 'Done'), ('Graded', 'Graded'), ('Drop Requested', 'Drop Requested'), ('Dropped', 'Dropped'), ('Waitlisted', 'Waitlisted')], default='Registered', max_length=20, verbose_name='Student Status')),
                ('section', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sis.section')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sis.student')),
            ],
            options={
                'ordering': ['section', 'student'],
                'unique_together': {('section', 'student')},
            },
        ),
        migrations.AddField(
            model_name='section',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis.semester'),
        ),
        migrations.AddField(
            model_name='section',
            name='students',
            field=models.ManyToManyField(related_name='section_students', through='sis.SectionStudent', to='sis.Student'),
        ),
        migrations.AddField(
            model_name='major',
            name='professors',
            field=models.ManyToManyField(blank=True, related_name='prof', to='sis.Professor'),
        ),
        migrations.CreateModel(
            name='CoursePrerequisite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='a_course', to='sis.course')),
                ('prerequisite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='a_prerequisite', to='sis.course')),
            ],
            options={
                'ordering': ['course', 'prerequisite'],
                'unique_together': {('course', 'prerequisite')},
            },
        ),
        migrations.AddField(
            model_name='course',
            name='major',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis.major'),
        ),
        migrations.AddField(
            model_name='course',
            name='prereqs',
            field=models.ManyToManyField(through='sis.CoursePrerequisite', to='sis.Course'),
        ),
        migrations.CreateModel(
            name='TranscriptRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_requested', models.DateField(verbose_name='Date Requested')),
                ('date_fulfilled', models.DateField(blank=True, null=True, verbose_name='Date Fulfilled')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis.student')),
            ],
            options={
                'ordering': ['student'],
                'unique_together': {('student', 'date_requested')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='semesterstudent',
            unique_together={('semester', 'student')},
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together={('course', 'semester', 'number')},
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('major', 'catalog_number')},
        ),
    ]
