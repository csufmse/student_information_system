# Generated by Django 3.1.7 on 2021-03-08 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0003_auto_20210308_0634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='capabilities',
        ),
        migrations.AddField(
            model_name='role',
            name='users',
            field=models.ManyToManyField(to='sis.Person'),
        ),
    ]
