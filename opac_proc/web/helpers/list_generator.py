# coding: utf-8
def get_generic_list_view():
    return [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Deleted?',
            'field_name': 'is_deleted',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'must_reprocess',
            'field_type': 'boolean'
        },
    ]


def get_log_columns_list_view():
    return [
        {
            'field_label': u'Timestamp',
            'field_name': 'time',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Name',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'Function',
            'field_name': 'funcName',
            'field_type': 'string'
        },
        {
            'field_label': u'Message',
            'field_name': 'message',
            'field_type': 'string'
        },
        {
            'field_label': u'Line',
            'field_name': 'lineno',
            'field_type': 'string'
        },
        {
            'field_label': u'Level',
            'field_name': 'levelname',
            'field_type': 'string'
        },
    ]


def get_log_filters_list_view():
    return [
        {
            'field_label': u'Timestamp',
            'field_name': 'time',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Name',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'Function',
            'field_name': 'funcName',
            'field_type': 'string'
        },
        {
            'field_label': u'Message',
            'field_name': 'message',
            'field_type': 'string'
        },
        {
            'field_label': u'Level',
            'field_name': 'levelname',
            'field_type': 'choices',
            'field_options': (
                ('DEBUG', 'DEBUG'),
                ('INFO', 'INFO'),
                ('WARNING', 'WARNING'),
                ('ERROR', 'ERROR'),
                ('CRITICAL', 'CRITICAL'),
            )
        },
    ]


def get_collection_list_view():
    list = get_generic_list_view()

    list.insert(1, {
        'field_label': u'Acrônimo',
        'field_name': 'acronym',
        'field_type': 'string'
    })

    list.insert(2, {
        'field_label': u'Nome',
        'field_name': 'name',
        'field_type': 'string'
    })
    return list


def get_journal_list_view():
    list = get_generic_list_view()

    list.insert(1, {
            'field_label': u'ISSN',
            'field_name': 'code',
            'field_type': 'string'
        })
    return list


def get_issue_list_view():
    list = get_generic_list_view()

    list.insert(1, {
            'field_label': u'PID',
            'field_name': 'code',
            'field_type': 'string'
        })
    return list


def get_article_list_view():
    list = get_generic_list_view()

    list.insert(1, {
            'field_label': u'PID',
            'field_name': 'code',
            'field_type': 'string'
        })
    return list


def get_press_release_list_view():
    return get_generic_list_view()
