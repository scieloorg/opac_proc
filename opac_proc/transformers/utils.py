# coding: utf-8

import datetime


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
