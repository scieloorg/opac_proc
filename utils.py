# coding: utf-8

import datetime
import requests

import config


def trydate(str_date):
    """
    Try to convert like string date to datetime.

    Possibilities: 2010, 2010-10, 2010-1-2
    """
    list_date = str_date.split('-')

    if len(list_date) == 1:
        return datetime.datetime.strptime(str_date, '%Y')
    elif len(list_date) == 2:
        return datetime.datetime.strptime(str_date, '%Y-%M')
    elif len(list_date) == 3:
        return datetime.datetime.strptime(str_date, '%Y-%M-%d')


def split_list(li, col):
    return [li[i:i+col] for i in range(0, len(li), col)]


def do_request_json(url, params):
    try:
        response = requests.get(url, params=params)
    except:
        return {}
    if response.status_code == 200:
        return response.json()
    return {}

def generate_filename(filename, lang, extension):
    """
    Return something like this: ``1678-4464-csp-32-07-e00107014_pt.xml``
    """
    return '{0}_{1}.{2}'.format(filename, lang, extension)

