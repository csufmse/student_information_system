import django_tables2 as tables
import types


# Each column and cell has its own CSS class based on the type of
# data in it.
def field_css_classes(field_name):
    return {'th': {'class': field_name + '_col'}, 'td': {'class': field_name + '_cell'}}


# mix in a method to get specified CSS row class. Used by filtered_table2
def row_class(cls):
    ra = getattr(cls, 'Meta').row_attrs
    rowc = ra['class']
    # for message tables, there are record-dependent classes
    if isinstance(rowc, types.LambdaType):
        rowc = rowc(None)
    return rowc


tables.Table.row_class = classmethod(row_class)
