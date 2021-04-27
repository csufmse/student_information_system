import django_tables2 as tables


# Each column and cell has its own CSS class based on the type of
# data in it.
def field_css_classes(field_name):
    return {'th': {'class': field_name + '_col'}, 'td': {'class': field_name + '_cell'}}


# mix in a method to get specified CSS row class. Used by filtered_table2
def row_class(cls):
    ra = getattr(cls, 'Meta').row_attrs
    return ra['class']


tables.Table.row_class = classmethod(row_class)


# mix in a method to get specified CSS row class. Used by filtered_table2
def row_class(cls):
    ra = getattr(cls, 'Meta').row_attrs
    return ra['class']


tables.Table.row_class = classmethod(row_class)
