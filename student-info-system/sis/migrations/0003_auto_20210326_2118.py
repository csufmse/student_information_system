# Generated by Django 3.1.7 on 2021-03-26 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0002_auto_20210326_0713'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admin',
            options={'ordering': ['user__username']},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['major', 'catalog_number', 'title']},
        ),
        migrations.AlterModelOptions(
            name='courseprerequisite',
            options={'ordering': ['course', 'prerequisite']},
        ),
        migrations.AlterModelOptions(
            name='professor',
            options={'ordering': ['user__username']},
        ),
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ['semester', 'course', 'number']},
        ),
        migrations.AlterModelOptions(
            name='sectionstudent',
            options={'ordering': ['section', 'student']},
        ),
        migrations.AlterModelOptions(
            name='semester',
            options={'ordering': ['date_registration_opens']},
        ),
        migrations.AlterModelOptions(
            name='semesterstudent',
            options={'ordering': ['semester', 'student']},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ['user__username']},
        ),
        migrations.AlterModelOptions(
            name='transcriptrequest',
            options={'ordering': ['student']},
        ),
    ]