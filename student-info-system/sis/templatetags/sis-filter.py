from django import template


register = template.Library()


@register.inclusion_tag('sis/sis-filter.html',takes_context=True)
def sis_filter(context, filt, destination):
    """Uses django-filter and bootstrap. Requires a filter "group name", and
       the destination url for the page"""

    context = {
        'filt' : context[filt],
        'destination': destination,
        'request': context['request'],
    }
    return context
    
