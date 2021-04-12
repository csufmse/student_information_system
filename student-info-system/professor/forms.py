from django.forms import ModelForm

from sis.models import ReferenceItem


class ReferenceItemForm(ModelForm):

    class Meta:
        model = ReferenceItem
        fields = ['title', 'description', 'link', 'edition', 'isbn', 'type']
