from django import template


register = template.Library()

@register.inclusion_tag('sis/sis-filter-tag.html')
def sis_filter_tag(filt, has_filter, destination):
    """Uses django-filter and bootstrap. Requires a filter, has_filter bool, and 
       the destination url for the page"""

    context = {
        'filt': filt,
        'has_filter': has_filter,
        'destination': destination
    }
    return context
    
