# Generated by Django 3.1.7 on 2021-03-29 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0004_remove_student_sections'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='major',
            options={'ordering': ['abbreviation']},
        ),
    ]