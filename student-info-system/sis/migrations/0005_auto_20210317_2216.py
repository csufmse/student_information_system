# Generated by Django 3.1.7 on 2021-03-17 22:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0004_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semester',
            name='name',
        ),
        migrations.AddField(
            model_name='semester',
            name='semester',
            field=models.CharField(choices=[('FA', 'Fall'), ('SP', 'Spring'), ('SU', 'Summer'), ('WI', 'Winter')], default='FA', max_length=2, verbose_name='semester'),
        ),
        migrations.AddField(
            model_name='semester',
            name='year',
            field=models.IntegerField(default=2000, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2300)], verbose_name='year'),
        ),
    ]