from datetime import date, datetime
import pytz
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from sis.models import (Profile, Major, Message, SectionStudent, Student)

from sis.utils import filtered_table, filtered_table2, DUMMY_ID

from sis.filters.message import (FullSentMessageFilter, FullReceivedMessageFilter,
                                 SentMessageFilter, ReceivedMessageFilter)
from sis.tables.messages import (MessageSentTable, MessageReceivedTable,
                                 StudentMessageReceivedTable)
from schooladmin.views import transcript


@login_required
def usermessages(request):
    the_user = request.user

    sentFilter = FullSentMessageFilter
    receivedFilter = FullReceivedMessageFilter
    receivedTable = MessageReceivedTable
    if the_user.profile.role == Profile.ACCESS_STUDENT:
        sentFilter = SentMessageFilter
        receivedFilter = ReceivedMessageFilter
        receivedTable = StudentMessageReceivedTable

    data = {
        'auser': the_user,
    }
    data.update(
        filtered_table(
            name='received',
            qs=the_user.profile.sent_to.all(),
            filter=receivedFilter,
            table=receivedTable,
            request=request,
            wrap_list=False,
        ))
    data.update(
        filtered_table(
            name='sent',
            qs=the_user.profile.sent_by.all(),
            filter=sentFilter,
            table=MessageSentTable,
            request=request,
            wrap_list=False,
        ))

    return render(request, 'sis/messages.html', data)


@login_required
def message(request, id):
    the_user = request.user
    the_profile = the_user.profile

    the_mess = Message.objects.get(id=id)
    is_recipient = the_mess.recipient == the_profile
    is_sender = the_mess.sender == the_profile
    is_student = the_profile.role == Profile.ACCESS_STUDENT
    is_admin = the_profile.role == Profile.ACCESS_ADMIN
    can_reply = the_mess.recipient == the_profile and not is_sender

    if the_mess is None:
        messages.error(request, 'Invalid message')
        return redirect('sis:messages')

    if not (is_sender or is_recipient) and not is_admin:
        messages.error(request, 'Invalid message')

    if request.method == 'POST':
        if request.POST.get('unarchive', None) is not None:
            messages.success(request, 'Message unarchived.')
            the_mess.time_archived = None
            the_mess.save()

        elif request.POST.get('archive', None) is not None:
            messages.success(request, 'Message archived.')
            the_mess.time_archived = datetime.now(pytz.utc)
            the_mess.save()

        elif request.POST.get('reply', None) is not None:
            messages.success(request, 'Trust me, you replied.')

        elif is_admin and request.POST.get('approvedrop', None) is not None:
            the_student = Student.objects.get(id=the_mess.support_data['student'])
            the_ssect = SectionStudent.objects.get(id=the_mess.support_data['section'])
            the_student.drop_approved(sectionstudent=the_ssect, request_message=the_mess)
            messages.success(request, 'Drop Approved.')

        elif is_admin and request.POST.get('rejectdrop', None) is not None:
            the_mess.time_handled = datetime.now(pytz.utc)
            the_mess.save()
            messages.success(request, 'Trust me, you rejected the drop.')

        elif is_admin and request.POST.get('approvemajor', None) is not None:
            the_student = Student.objects.get(id=the_mess.support_data['student'])
            the_new_major = Major.objects.get(id=the_mess.support_data['major'])
            the_student.major_change_approved(major=the_new_major, request_message=the_mess)
            messages.success(request, 'Major Change Approved.')

        elif is_admin and request.POST.get('rejectmajor', None) is not None:
            the_mess.time_handled = datetime.now(pytz.utc)
            the_mess.save()
            messages.success(request, 'Trust me, you rejected the major change.')

        elif is_admin and request.POST.get('transcriptreq', None) is not None:
            the_mess.time_handled = datetime.now(pytz.utc)
            the_mess.save()
            the_student = Student.objects.get(id=the_mess.support_data['student'])
            response = Message.objects.create(
                sender=the_profile,
                recipient=the_student.profile,
                message_type=Message.TRANSCRIPT_TYPE,
                subject="Your Transcript",
                body="I'll be emailing it to you.",
                in_response_to=the_mess,
            )
            messages.success(request, 'Transcript promised.')
            the_student = Student.objects.get(id=the_mess.support_data['student'])
            # this generates and downloads the file.
            return transcript(request, userid=the_student.profile.user.id)

        else:
            messages.error(request, 'Something went wrong.')

    # mark our received messages read. Don't touch sent messages.
    if is_recipient and the_mess.time_read is None:
        the_mess.time_read = datetime.now(pytz.utc)
        the_mess.save()

    handled = the_mess.time_handled is not None
    handleable_message = the_mess.message_type in (Message.DROP_REQUEST_TYPE,
                                                   Message.MAJOR_CHANGE_TYPE)
    show_drop = is_recipient and the_mess.message_type == Message.DROP_REQUEST_TYPE \
        and not handled
    show_major = is_recipient and the_mess.message_type == Message.MAJOR_CHANGE_TYPE \
        and not handled
    show_transcript_req = is_recipient \
        and the_mess.message_type == Message.TRANSCRIPT_REQUEST_TYPE \
        and not handled
    return render(
        request, 'sis/message.html', {
            'auser': the_user,
            'message': the_mess,
            'show_approve_drop': show_drop,
            'show_approve_major': show_major,
            'show_transcript_req': show_transcript_req,
            'show_archive': is_recipient,
            'message_archived': the_mess.time_archived is not None,
            'message_read': the_mess.time_read is not None,
            'message_handled': handled,
            'show_type': not is_student,
            'show_handled': handleable_message and not is_student,
            'show_read': True,
            'can_reply': can_reply
        })
