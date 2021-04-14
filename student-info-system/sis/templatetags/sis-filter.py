from django import template

register = template.Library()


@register.inclusion_tag('sis/sis-filter.html', takes_context=True)
def sis_filter(context, filt):
    newcontext = {
        'request': context['request'],
    }
    if filt in context:
        newcontext['filt'] = context[filt]
    return newcontext
