import django_tables2 as tables


# Each column and cell has its own CSS class based on the type of
# data in it.
def field_css_classes(field_name):
    return {'th': {'class': field_name + '_col'}, 'td': {'class': field_name + '_cell'}}


class ClassyColumn(tables.Column):

    def __init__(self, *args, **kwargs):
        if 'css_class_base' in kwargs:
            css_class_base = kwargs.pop('css_class_base', None)
            kwargs['attrs'] = field_css_classes(css_class_base)
        super(ClassyColumn, self).__init__(*args, **kwargs)


class ClassyBooleanColumn(tables.BooleanColumn):

    def __init__(self, *args, **kwargs):
        if 'css_class_base' in kwargs:
            css_class_base = kwargs.pop('css_class_base', None)
            kwargs['attrs'] = field_css_classes(css_class_base)
        super(ClassyBooleanColumn, self).__init__(*args, **kwargs)


# For User names we want to show the full name ("first last") but sort by "last, first"
class NameColumn(ClassyColumn):

    def render(self, record):
        return record.name

    def order(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "name_sort")
        return (queryset, True)


class AbilityColumn(tables.BooleanColumn):
    header = "Enabled?"
