from django import template

register = template.Library()


@register.inclusion_tag('sis/sis-filter.html', takes_context=True)
def sis_filter(context, filt):
    context = {
        'filt': context[filt],
        'request': context['request'],
    }
    return context
