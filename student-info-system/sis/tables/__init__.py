import django_tables2 as tables


# mix in a method to get specified CSS row class. Used by filtered_table2
def row_class(cls):
    ra = getattr(cls, 'Meta').row_attrs
    return ra['class']


tables.Table.row_class = classmethod(row_class)


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


class ClassyDateTimeColumn(tables.DateTimeColumn):

    def __init__(self, *args, **kwargs):
        if 'css_class_base' in kwargs:
            css_class_base = kwargs.pop('css_class_base', None)
            kwargs['attrs'] = field_css_classes(css_class_base)
        super(ClassyDateTimeColumn, self).__init__(*args, **kwargs)


class AbilityColumn(tables.BooleanColumn):
    header = "Enabled?"
