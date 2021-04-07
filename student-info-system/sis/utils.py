from django_tables2 import RequestConfig


# helper function to make tables
# merge the result of this into the response data
def filtered_table(name=None,
                   qs=None,
                   filter=None,
                   table=None,
                   request=None,
                   page_size=25,
                   wrap_list=True):
    if filter:
        filt = filter(request.GET, queryset=qs, prefix=name)
        # weird "{name}" thing is because the HTML field has the prefix but the Filter does
        # NOT have it in the field names
        has_filter = any(f'{name}-{field}' in request.GET for field in set(filt.get_fields()))
        table_source = filt.qs
        print(f'{filt}')
    else:
        filt = None
        has_filter = False
        table_source = qs
    if wrap_list:
        table_source = list(table_source)
    tab = table(table_source, prefix=name + "-")
    RequestConfig(request, paginate={"per_page": page_size, "page": 1}).configure(tab)
    return {name + '_table': tab, name + '_filter': filt, name + '_has_filter': has_filter}
