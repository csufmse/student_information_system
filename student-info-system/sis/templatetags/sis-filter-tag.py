from django import template


register = template.Library()

@register.inclusion_tag('sis_filter_tag.html')
def sis_filter_tag(filt, has_filter, table, url, *args):
    """Uses django-filter, django_tables2, and bootstrap. Requires a filter, filter values set,
    table, the destination url for the page, and optional args for the destination url."""

    context = {
        'filt': filt,
        'has_filter': has_filter,
        'table': table,
        'dest': { 'url': url, 'args': [x for x in args] }
    }
    return context
    
