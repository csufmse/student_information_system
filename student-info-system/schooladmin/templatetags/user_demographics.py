from django import template

register = template.Library()


@register.inclusion_tag('demo.html')
def demographic_details(profile):
    return {
        'profile': profile,
    }
