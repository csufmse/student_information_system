from django_tables2 import RequestConfig

# used as dummy in addClickHandler
DUMMY_ID = 1234599


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
    else:
        filt = None
        has_filter = False
        table_source = qs
    if wrap_list:
        table_source = list(table_source)
    tab = table(table_source, prefix=name + "-")
    RequestConfig(request, paginate={"per_page": page_size, "page": 1}).configure(tab)
    return {name + '_table': tab, name + '_filter': filt, name + '_has_filter': has_filter}


def filtered_table2(name=None,
                    qs=None,
                    filter=None,
                    table=None,
                    request=None,
                    page_size=25,
                    row_class=None,
                    self_url=None,
                    click_url=None,
                    scrollable=False,
                    table_type='data-table-alt',
                    wrap_list=True):
    if row_class is None:
        # "table" is the class, for which we added...
        row_class = table.row_class()
    filt = filter(request.GET, queryset=qs, prefix=name)
    # weird "{name}" thing is because the HTML field has the prefix but the Filter does
    # NOT have it in the field names
    has_filter = any(f'{name}-{field}' in request.GET for field in set(filt.get_fields()))
    table_source = filt.qs
    if wrap_list:
        table_source = list(table_source)
    tab = table(table_source, prefix=name + "-")
    div_classes = table_type
    if scrollable:
        div_classes += ' scrollify-me'
    RequestConfig(request, paginate={"per_page": page_size, "page": 1}).configure(tab)
    return {
        name: {
            'name': name,
            'table': tab,
            'filter': filt,
            'has_filter': has_filter,
            'self_url': self_url,
            'click_url': click_url,
            'row_class': row_class,
            'div_classes': div_classes,
        }
    }


def ssects_by_sem(user):
    qs = user.profile.student.course_history().order_by('section__semester')
    ssects_by_sem = None
    if len(qs):
        ssects_by_sem = [[qs[0]]]
        i = 0
        for ssect in qs:
            if ssect.section.semester == ssects_by_sem[i][0].section.semester:
                ssects_by_sem[i].append(ssect)
            else:
                i += 1
                ssects_by_sem.insert(i, [ssect])
    return ssects_by_sem
