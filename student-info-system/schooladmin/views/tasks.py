from django.contrib import messages
from django.shortcuts import render

from sis.authentication_helpers import role_login_required

from sis.models import Interval, Profile, Task, Tasks, AcademicProbationTask

from sis.elements.task import AcademicProbationTaskForm, IntervalForm


@role_login_required(Profile.ACCESS_ADMIN)
def tasks(request):
    tasks = Tasks.objects.all()
    return render(request, 'schooladmin/tasks.html', {'tasks': tasks})


@role_login_required(Profile.ACCESS_ADMIN)
def task_edit(request, taskid=None):
    interval_options = Interval.INTERVAL_TYPES
    interval = None
    if request.method == 'POST' and not taskid:
        form = AcademicProbationTaskForm(request.POST)
        if request.POST['frequency_type'] == Task.INTERVAL:
            i_type = request.POST['interval_type']
            i_amt = request.POST['interval_amount']
            interval = Interval.objects.create(interval_type=i_type, interval_amount=i_amt)
            form.instance.interval = interval
        try:
            task = form.save()
            messages.success(request, 'Successfully created a task')
        except ValueError as e:
            messages.error(request, 'Please correct the following fields.')
            return render(request, 'schooladmin/task_edit.html', {
                'form': form,
                'options': interval_options
            })
        Tasks.add_task(task)
    elif request.method == 'POST':
        tasks_obj = Tasks.objects.get(pk=taskid)
        ap_task = AcademicProbationTask.objects.get(pk=tasks_obj.task.pk)
        form = AcademicProbationTaskForm(request.POST, instance=ap_task)
        if form.is_valid():
            updated_task = form.save(commit=False)
            updated_task.save()
            form.save_m2m()
            tasks_obj.task = updated_task
            tasks_obj.save()
            messages.success(request, "Task updated successfully")
            return tasks(request)
    else:
        if taskid:
            instance = Tasks.objects.get(pk=taskid)
            interval = instance.task.interval
            form = AcademicProbationTaskForm(instance=instance.task)
        else:
            form = AcademicProbationTaskForm()
    return render(request, 'schooladmin/task_edit.html', {
        'form': form,
        'options': interval_options,
        'interval': interval
    })
