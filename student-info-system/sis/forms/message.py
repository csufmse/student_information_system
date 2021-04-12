from django import forms

from sis.models import (Message)
from sis.forms.utils import *


class MessageDetailForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.ROLES,
                             required=True,
                             help_text='Select type of user')
    role.widget.attrs.update({'class': 'role_sel selectpicker'})

    bio = forms.CharField(max_length=256,
                          required=False,
                          widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Profile
        fields = ('role', 'bio')
