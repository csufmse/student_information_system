from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from sis.models import (SectionReferenceItem)


def sectionreferenceitem(request, id):
    qs = SectionReferenceItem.objects.filter(id=id)
    if qs.count() < 1:
        return HttpResponse("No such sectionreferenceitem")
    the_sri = qs[0]

    data = {
        'section': the_sri.section,
        'item': the_sri.item,
        'index': the_sri.index,
    }
    return render(request, 'sis/sectionreferenceitem.html', data)
