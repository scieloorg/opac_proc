# coding: utf-8

import re
import datetime


def trydate(str_date):
    """
    Try to convert like string date to datetime.

    Possibilities: 2010, 2010-10, 2010-1-2
    """

    if str_date is None:
        ValueError('Invalid date.')

    list_date = str_date.split('-')

    if len(list_date) == 1:
        return datetime.datetime.strptime(str_date, '%Y')
    elif len(list_date) == 2:
        return datetime.datetime.strptime(str_date, '%Y-%M')
    elif len(list_date) == 3:
        return datetime.datetime.strptime(str_date, '%Y-%M-%d')


def validate_email(email):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param email:
        ValueError email to raise in case of a validation error.

    Return:

        Return None if the string does not match the pattern; note that this
        is different from a zero-length match.
    """

    if email is None:
        ValueError('Invalid email address.')

    regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)

    return regex.match(email)
