# coding: utf-8
import maya

MODEL_NAME_LIST = [
    'collection',
    'journal',
    'issue',
    'article',
    'news',
    'press_release'
]

STAGE_LIST = [
    'extract',
    'transform',
    'load'
]

ACTION_LIST = [
    'add',
    'update',
    'delete'
]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def parse_journal_issn_from_issue_code(code):
    if code[0] == 'S':
        issn = code[0:10]
    else:
        issn = code[0:9]
    return issn


def parse_journal_issn_from_article_code(code):
    if code[0] == 'S':
        issn = code[0:10]
    else:
        issn = code[0:9]
    return issn


def parse_issue_pid_from_article_code(code):
    if code[0] == 'S':
        issue_pid = code[0:18]
    else:
        issue_pid = code[0:17]
    return issue_pid


def parse_date_str_to_datetime_obj(date_str):
    return maya.MayaDT.from_iso8601(date_str).datetime()
