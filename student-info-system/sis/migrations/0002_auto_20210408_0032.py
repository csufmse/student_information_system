# Generated by Django 3.1.7 on 2021-04-08 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionstudent',
            name='grade',
            field=models.SmallIntegerField(blank=True, choices=[(5, 'None'), (4, 'A'), (3, 'B'), (2, 'C'), (1, 'D'), (0, 'F')], default=5, null=True),
        ),
    ]